#!/usr/bin/env bash
set -u

. .venv/bin/activate

RUFF_STATUS=0
SONAR_STATUS=0

echo "Running Ruff code quality checks..."
ruff check . \
  --exclude .venv \
  --exclude __pycache__ \
  --exclude .git || RUFF_STATUS=$?

echo "Preparing SonarScanner CLI..."

SCANNER_VERSION=8.0.1.6346
SCANNER_DIR="$WORKSPACE/.sonar/sonar-scanner-$SCANNER_VERSION-linux-x64"

mkdir -p "$WORKSPACE/.sonar"

if [ ! -d "$SCANNER_DIR" ]; then
    echo "Downloading SonarScanner CLI..."
    curl -sSLo "$WORKSPACE/.sonar/sonar-scanner.zip" \
      "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SCANNER_VERSION-linux-x64.zip"

    unzip -o "$WORKSPACE/.sonar/sonar-scanner.zip" -d "$WORKSPACE/.sonar"
fi

echo "Running SonarCloud analysis..."
"$SCANNER_DIR/bin/sonar-scanner" -Dsonar.token="$SONAR_TOKEN" || SONAR_STATUS=$?

echo "Ruff exit code: $RUFF_STATUS"
echo "SonarCloud exit code: $SONAR_STATUS"

if [ "$RUFF_STATUS" -ne 0 ] || [ "$SONAR_STATUS" -ne 0 ]; then
    echo "Code Quality stage completed with findings or warnings."
    exit 1
fi

echo "Code Quality stage completed successfully."
