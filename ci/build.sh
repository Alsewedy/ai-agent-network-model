#!/usr/bin/env bash
set -euo pipefail

echo "Building application version: $APP_VERSION"

echo "Creating Python virtual environment..."
python3 -m venv .venv

echo "Installing Python dependencies..."
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ -f requirements-dev.txt ]; then
    echo "Installing CI/development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "Building Docker image artifact..."
docker build \
  -t "$IMAGE_NAME:$APP_VERSION" \
  -t "$IMAGE_NAME:latest" .

echo "Build stage completed successfully."
echo "Created Docker image artifact: $IMAGE_NAME:$APP_VERSION"
