#!/usr/bin/env bash
set -u

. .venv/bin/activate

PIP_AUDIT_STATUS=0
BANDIT_STATUS=0
TRIVY_STATUS=0

echo "Running dependency vulnerability scan with pip-audit..."
pip-audit -r requirements.txt || PIP_AUDIT_STATUS=$?

echo "Running Python source-code security scan with Bandit..."
bandit -r . \
  -x ./.venv,./tests,./__pycache__,./.git,./.sonar || BANDIT_STATUS=$?

echo "Running Docker image vulnerability scan with Trivy..."
echo "Scanning image: $IMAGE_NAME:$APP_VERSION"

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  "$IMAGE_NAME:$APP_VERSION" || TRIVY_STATUS=$?

echo "pip-audit exit code: $PIP_AUDIT_STATUS"
echo "Bandit exit code: $BANDIT_STATUS"
echo "Trivy exit code: $TRIVY_STATUS"

if [ "$PIP_AUDIT_STATUS" -ne 0 ] || [ "$BANDIT_STATUS" -ne 0 ] || [ "$TRIVY_STATUS" -ne 0 ]; then
    echo "Security stage completed with findings."
    exit 1
fi

echo "Security stage completed successfully."
