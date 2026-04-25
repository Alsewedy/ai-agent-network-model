#!/usr/bin/env bash
set -euo pipefail

. .venv/bin/activate
export OPENAI_API_KEY="$OPENAI_API_KEY"

echo "Running automated tests..."
pytest tests -v

echo "Test stage completed successfully."
