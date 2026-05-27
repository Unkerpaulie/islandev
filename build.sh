#!/usr/bin/env bash
# First-deploy script for islandev. Run once on a fresh server.
# Idempotent: safe to run more than once.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$REPO_DIR")"
VENV_DIR="$ROOT_DIR/.venv"

# 1. Source .env so DJANGO_SETTINGS_MODULE and friends are exported.
set -a
# shellcheck source=/dev/null
source "$ROOT_DIR/.env"
set +a

# 2. Create the venv if it does not already exist.
if [ ! -d "$VENV_DIR" ]; then
  python3.12 -m venv "$VENV_DIR"
fi

# 3. Install dependencies.
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"

# 4. Migrate.
python "$REPO_DIR/manage.py" migrate --noinput

# 5. Collect static files into <islandev_root>/staticfiles/.
python "$REPO_DIR/manage.py" collectstatic --noinput

# 6. Restart the Gunicorn service named in .env.
sudo systemctl restart "$GUNICORN_SERVICE_NAME"

echo "build.sh: complete."
