#!/usr/bin/env bash
set -euo pipefail

echo "Creating testing environment file..."

cat > .env.test <<EOF_ENV
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4-mini
APP_ENV=test
DEBUG=true
EOF_ENV

echo "Deploying Docker image to testing environment: $IMAGE_NAME:$APP_VERSION"

APP_VERSION="$APP_VERSION" docker compose -p ai-agent-test -f docker-compose.test.yml down --remove-orphans || true
docker rm -f ai-agent-test || true
APP_VERSION="$APP_VERSION" docker compose -p ai-agent-test -f docker-compose.test.yml up -d --force-recreate

echo "Validating testing environment health..."

for i in 1 2 3 4 5 6 7 8 9 10; do
    if curl --fail "$TEST_URL"; then
        echo "Testing environment is healthy."
        echo "Deploy stage completed successfully."
        exit 0
    fi

    echo "Waiting for testing environment to become ready..."
    sleep 3
done

echo "Testing environment failed to become healthy."
docker logs ai-agent-test || true
exit 1
