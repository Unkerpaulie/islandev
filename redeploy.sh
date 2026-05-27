#!/usr/bin/env bash
# Incremental redeploy for islandev. Run on every push to main.
# A failed test suite aborts the deploy: previous Gunicorn process stays live.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$REPO_DIR")"
VENV_DIR="$ROOT_DIR/.venv"

# 1. Source .env.
set -a
# shellcheck source=/dev/null
source "$ROOT_DIR/.env"
set +a

# 2. Pull the latest code on main.
cd "$REPO_DIR"
git pull --ff-only origin main

# 3. Sync dependencies.
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install -r "$REPO_DIR/requirements.txt"

# 4. Migrate.
python "$REPO_DIR/manage.py" migrate --noinput

# 5. Run the full test suite. Any failure aborts the deploy.
python "$REPO_DIR/manage.py" test --noinput

# 6. Collect static files.
python "$REPO_DIR/manage.py" collectstatic --noinput

# 7. Restart Gunicorn.
sudo systemctl restart "$GUNICORN_SERVICE_NAME"

echo "redeploy.sh: complete."
