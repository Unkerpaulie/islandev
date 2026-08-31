#!/usr/bin/env bash
# =============================================================================
# Build Script for Islan.DEV
# =============================================================================
# First-deploy script. Idempotent — safe to run more than once.
#
# Prerequisites:
#   - Run as the project owner user (islan_admin)
#   - .env must exist at <islandev_root>/.env (one level above this script)
#   - Git repo already cloned to <islandev_root>/islandev/
#   - Tailwind CSS built: ./tailwindcss -i ./static/src/input.css -o ./static/css/site.css --minify
#
# Usage:
#   cd /var/www/islandev_root/islandev
#   ./build.sh
# =============================================================================

set -o errexit
set -o pipefail

# =============================================================================
# Paths
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"   # islandev_root/

cd "$SCRIPT_DIR"

# =============================================================================
# Load Environment
# =============================================================================

if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/.env"
    set +a
    echo "✓ Loaded environment variables from $PROJECT_ROOT/.env"
else
    echo "✗ No .env found at $PROJECT_ROOT/.env"
    echo "  Copy .env.example to $PROJECT_ROOT/.env and fill in all values."
    exit 1
fi

# =============================================================================
# Defaults
# =============================================================================

DJANGO_ENV="${DJANGO_ENV:-production}"
VENV_PATH="${VENV_PATH:-.venv}"
GUNICORN_SERVICE_NAME="${GUNICORN_SERVICE_NAME:-islandev}"
SERVER_NAME="${SERVER_NAME:-islan.dev}"
GUNICORN_PORT="${GUNICORN_PORT:-8000}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"

# Colour codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_section() { echo ""; echo "========================================="; echo "$1"; echo "========================================="; }
log_info()    { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error()   { echo -e "${RED}✗${NC} $1"; }

# =============================================================================
# Step 1 — Install system packages
# =============================================================================

install_system_deps() {
    log_section "Step 1: Installing System Dependencies"

    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        nginx \
        certbot \
        python3-certbot-nginx \
        git

    log_success "System dependencies installed"
}

# =============================================================================
# Step 2 — Create directory structure
# =============================================================================

create_directories() {
    log_section "Step 2: Creating Directory Structure"

    mkdir -p "$PROJECT_ROOT/staticfiles"
    mkdir -p "$PROJECT_ROOT/media"
    mkdir -p "$PROJECT_ROOT/logs"

    log_success "Directories created:"
    log_info "  staticfiles → $PROJECT_ROOT/staticfiles"
    log_info "  media       → $PROJECT_ROOT/media"
    log_info "  logs        → $PROJECT_ROOT/logs"
}

# =============================================================================
# Step 3 — Set up PostgreSQL database
# =============================================================================

setup_database() {
    log_section "Step 3: Setting Up PostgreSQL Database"

    if [ -z "${DATABASE_URL:-}" ]; then
        log_warning "DATABASE_URL not set in .env — skipping database setup"
        return 0
    fi

    # Parse DATABASE_URL: postgres://user:password@host:port/dbname
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's|postgres://\([^:]*\):.*|\1|p')
    DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|postgres://[^:]*:\([^@]*\)@.*|\1|p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*$|\1|p')

    if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ]; then
        log_error "Could not parse DATABASE_URL — check format: postgres://user:pass@localhost:5432/dbname"
        exit 1
    fi

    log_info "Database: $DB_NAME  User: $DB_USER"

    # Create role if it doesn't exist
    sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" \
        | grep -q 1 \
        || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

    # Create database if it doesn't exist
    sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" \
        | grep -q 1 \
        || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

    # Ensure privileges (idempotent)
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

    # CREATEDB lets Django's test runner create test_<dbname> — remove if unwanted in prod
    sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

    log_success "Database '$DB_NAME' ready"
}

# =============================================================================
# Step 4 — Python virtual environment & dependencies
# =============================================================================

install_python_deps() {
    log_section "Step 4: Installing Python Dependencies"

    VENV_DIR="$PROJECT_ROOT/$VENV_PATH"

    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        log_info "Creating virtual environment at $VENV_DIR ..."
        python3.12 -m venv "$VENV_DIR"
    else
        log_info "Virtual environment already exists — reusing"
    fi

    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel --quiet
    pip install -r requirements.txt --quiet

    log_success "Python dependencies installed"
}

# =============================================================================
# Step 5 — Database migrations
# =============================================================================

run_migrations() {
    log_section "Step 5: Running Migrations"

    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/$VENV_PATH/bin/activate"

    python manage.py migrate --noinput || {
        log_error "Migrations failed"
        exit 1
    }

    log_success "Migrations completed"
}

# =============================================================================
# Step 6 — Collect static files
# =============================================================================

collect_static() {
    log_section "Step 6: Collecting Static Files"

    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/$VENV_PATH/bin/activate"

    python manage.py collectstatic --noinput --clear || {
        log_error "collectstatic failed"
        exit 1
    }

    log_success "Static files collected → $PROJECT_ROOT/staticfiles"
}

# =============================================================================
# Step 7 — Gunicorn systemd service
# =============================================================================

setup_systemd_service() {
    log_section "Step 7: Setting Up Gunicorn Systemd Service"

    SERVICE_FILE="/etc/systemd/system/${GUNICORN_SERVICE_NAME}.service"
    VENV_DIR="$PROJECT_ROOT/$VENV_PATH"
    RUN_USER="$(whoami)"

    # Stop and remove existing service if present
    if systemctl list-unit-files 2>/dev/null | grep -q "^${GUNICORN_SERVICE_NAME}.service"; then
        log_warning "Service ${GUNICORN_SERVICE_NAME}.service already exists — replacing"
        sudo systemctl stop  "$GUNICORN_SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$GUNICORN_SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "$SERVICE_FILE"
    fi

    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Gunicorn instance serving Islan.DEV
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$RUN_USER
Group=www-data
WorkingDirectory=$SCRIPT_DIR
EnvironmentFile=$PROJECT_ROOT/.env
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers $GUNICORN_WORKERS \\
    --bind 127.0.0.1:$GUNICORN_PORT \\
    --access-logfile $PROJECT_ROOT/logs/access.log \\
    --error-logfile $PROJECT_ROOT/logs/error.log \\
    --capture-output \\
    --log-level warning \\
    islandev.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$GUNICORN_SERVICE_NAME"
    sudo systemctl start  "$GUNICORN_SERVICE_NAME"

    sleep 3

    if systemctl is-active --quiet "$GUNICORN_SERVICE_NAME"; then
        log_success "Gunicorn service '${GUNICORN_SERVICE_NAME}' is running"
    else
        log_error "Gunicorn failed to start — check logs:"
        log_info "  sudo journalctl -u $GUNICORN_SERVICE_NAME -n 50"
        exit 1
    fi
}

# =============================================================================
# Step 8 — Nginx configuration
# =============================================================================

setup_nginx() {
    log_section "Step 8: Configuring Nginx"

    NGINX_CONF="/etc/nginx/sites-available/${GUNICORN_SERVICE_NAME}"
    NGINX_LINK="/etc/nginx/sites-enabled/${GUNICORN_SERVICE_NAME}"

    sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME www.$SERVER_NAME;

    client_max_body_size 20M;

    # Static files — served directly by Nginx, bypasses Gunicorn entirely
    location /static/ {
        alias $PROJECT_ROOT/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files — user uploads
    location /media/ {
        alias $PROJECT_ROOT/media/;
        expires 7d;
    }

    # Everything else — proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

    # Enable site
    [ -L "$NGINX_LINK" ] && sudo rm "$NGINX_LINK"
    sudo ln -s "$NGINX_CONF" "$NGINX_LINK"

    # Remove default placeholder site
    sudo rm -f /etc/nginx/sites-enabled/default

    # Validate and reload
    sudo nginx -t || {
        log_error "Nginx config test failed — fix the error above and re-run"
        exit 1
    }
    sudo systemctl reload nginx

    log_success "Nginx configured for $SERVER_NAME"
}

# =============================================================================
# Main
# =============================================================================

main() {
    log_section "Islan.DEV Build Starting"
    log_info "Environment : $DJANGO_ENV"
    log_info "Settings    : $DJANGO_SETTINGS_MODULE"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Service     : $GUNICORN_SERVICE_NAME (port $GUNICORN_PORT)"
    log_info "Domain      : $SERVER_NAME"
    echo ""

    install_system_deps
    create_directories
    setup_database
    install_python_deps
    run_migrations
    collect_static
    setup_systemd_service
    setup_nginx

    log_section "✅ Build Completed Successfully"
    log_info "Next steps:"
    log_info "  1. Verify site over HTTP:  curl -I http://$SERVER_NAME"
    log_info "  2. Obtain SSL certificate: sudo certbot --nginx -d $SERVER_NAME -d www.$SERVER_NAME"
    log_info "  3. Create superuser:       source $PROJECT_ROOT/$VENV_PATH/bin/activate"
    log_info "                             python manage.py createsuperuser"
    echo ""
}

main
