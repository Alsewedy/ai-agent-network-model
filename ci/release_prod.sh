#!/usr/bin/env bash
set -euo pipefail

echo "Creating production environment file..."

cat > .env.production <<EOF_ENV
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4-mini
APP_ENV=production
DEBUG=false
EOF_ENV

echo "Releasing Docker image to production environment: $IMAGE_NAME:$APP_VERSION"

APP_VERSION="$APP_VERSION" docker compose -p ai-agent-prod -f docker-compose.prod.yml down --remove-orphans || true
docker rm -f ai-agent-prod || true
APP_VERSION="$APP_VERSION" docker compose -p ai-agent-prod -f docker-compose.prod.yml up -d --force-recreate

echo "Validating production environment health..."

HEALTHY=false

for i in 1 2 3 4 5 6 7 8 9 10; do
    if curl --fail "$PROD_URL"; then
        echo "Production environment is healthy."
        HEALTHY=true
        break
    fi

    echo "Waiting for production environment to become ready..."
    sleep 3
done

if [ "$HEALTHY" != "true" ]; then
    echo "Production release failed health validation."
    docker logs ai-agent-prod || true
    exit 1
fi

echo "Creating Git release tag..."

git config user.name "Jenkins CI"
git config user.email "jenkins-ci@example.local"

RELEASE_TAG="release-$APP_VERSION"

git fetch --tags || true

if git rev-parse "$RELEASE_TAG" >/dev/null 2>&1; then
    echo "Git tag $RELEASE_TAG already exists locally."
else
    git tag -a "$RELEASE_TAG" -m "Production release $APP_VERSION"
fi

echo "Pushing Git release tag to GitHub..."
git push "https://$GIT_USERNAME:$GIT_TOKEN@github.com/Alsewedy/ai-agent-network-model.git" "$RELEASE_TAG"

echo "Release stage completed successfully."
echo "Production release tag created: $RELEASE_TAG"
