#!/usr/bin/env bash
set -euo pipefail

echo "Starting production monitoring checks..."

REPORT_FILE="monitoring_report.txt"

{
    echo "=== AI Agent Production Monitoring Report ==="
    echo "Build Number: $BUILD_NUMBER"
    echo "Application Version: $APP_VERSION"
    echo "Production URL: $PROD_URL"
    echo "Generated At: $(date)"
    echo ""
} > "$REPORT_FILE"

echo "Checking production container status..."
docker ps --filter "name=ai-agent-prod" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | tee -a "$REPORT_FILE"

echo "" | tee -a "$REPORT_FILE"
echo "Checking production image version..." | tee -a "$REPORT_FILE"
docker inspect ai-agent-prod --format='Production image: {{.Config.Image}}' | tee -a "$REPORT_FILE"

echo "" | tee -a "$REPORT_FILE"
echo "Checking production health endpoint..." | tee -a "$REPORT_FILE"

if curl --fail --silent --show-error "$PROD_URL" | tee -a "$REPORT_FILE"; then
    echo "" | tee -a "$REPORT_FILE"
    echo "MONITORING STATUS: Production health check passed." | tee -a "$REPORT_FILE"
else
    echo "" | tee -a "$REPORT_FILE"
    echo "ALERT: Production health check failed." | tee -a "$REPORT_FILE"
    echo "Collecting production logs for troubleshooting..." | tee -a "$REPORT_FILE"
    docker logs --tail 50 ai-agent-prod | tee -a "$REPORT_FILE" || true
    exit 1
fi

echo "" | tee -a "$REPORT_FILE"
echo "Collecting recent production logs..." | tee -a "$REPORT_FILE"
docker logs --tail 30 ai-agent-prod | tee -a "$REPORT_FILE" || true

echo "" | tee -a "$REPORT_FILE"
echo "Collecting production container resource usage..." | tee -a "$REPORT_FILE"
docker stats ai-agent-prod --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | tee -a "$REPORT_FILE" || true

echo "" | tee -a "$REPORT_FILE"
echo "Monitoring stage completed." | tee -a "$REPORT_FILE"
