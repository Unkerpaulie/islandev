#!/usr/bin/env bash
# =============================================================================
# Redeploy Script for Islan.DEV
# =============================================================================
# Incremental update. Pulls latest code, syncs deps, runs migrations,
# optionally runs tests, collects static files, and restarts Gunicorn.
#
# Usage:
#   cd /var/www/islandev_root/islandev
#   ./redeploy.sh
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
    exit 1
fi

# =============================================================================
# Defaults
# =============================================================================

DJANGO_ENV="${DJANGO_ENV:-production}"
VENV_PATH="${VENV_PATH:-.venv}"
GUNICORN_SERVICE_NAME="${GUNICORN_SERVICE_NAME:-islandev}"

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
# Validation
# =============================================================================

validate_service() {
    log_section "Validating Service"

    if ! systemctl status "$GUNICORN_SERVICE_NAME" &>/dev/null; then
        log_error "Service '${GUNICORN_SERVICE_NAME}' not found"
        log_info "Run ./build.sh first to set up the service."
        exit 1
    fi

    log_success "Service '${GUNICORN_SERVICE_NAME}' exists"

    if systemctl is-active --quiet "$GUNICORN_SERVICE_NAME"; then
        CURRENT_PID=$(systemctl show -p MainPID "$GUNICORN_SERVICE_NAME" | cut -d= -f2)
        log_info "Currently running — PID $CURRENT_PID"
    else
        log_warning "Service exists but is not currently running"
    fi
}

# =============================================================================
# Step 1 — Pull latest code
# =============================================================================

pull_code() {
    log_section "Step 1: Pulling Latest Code"

    CURRENT_COMMIT=$(git rev-parse HEAD)
    BACKUP_BRANCH="pre-deploy-$(date +%Y%m%d-%H%M%S)"
    git branch "$BACKUP_BRANCH" "$CURRENT_COMMIT" 2>/dev/null || true
    log_info "Rollback branch: $BACKUP_BRANCH"
    log_info "To rollback:     git checkout $BACKUP_BRANCH && sudo systemctl restart $GUNICORN_SERVICE_NAME"

    git fetch origin
    git checkout main
    git pull --ff-only origin main || {
        log_error "Pull failed — possible merge conflict or non-fast-forward"
        log_info "Rollback: git checkout $BACKUP_BRANCH"
        exit 1
    }

    NEW_COMMIT=$(git rev-parse --short HEAD)
    COMMIT_MSG=$(git log -1 --pretty=%B | head -n 1)
    log_success "At commit $NEW_COMMIT — $COMMIT_MSG"
}

# =============================================================================
# Step 2 — Activate virtual environment
# =============================================================================

activate_venv() {
    log_section "Step 2: Activating Virtual Environment"

    VENV_ACTIVATE="$PROJECT_ROOT/$VENV_PATH/bin/activate"

    if [ ! -f "$VENV_ACTIVATE" ]; then
        log_error "Virtual environment not found at $PROJECT_ROOT/$VENV_PATH"
        log_info "Run ./build.sh first."
        exit 1
    fi

    # shellcheck source=/dev/null
    source "$VENV_ACTIVATE"
    log_success "Virtual environment activated"
}

# =============================================================================
# Step 3 — Sync Python dependencies
# =============================================================================

install_deps() {
    log_section "Step 3: Syncing Python Dependencies"

    pip install --upgrade pip setuptools wheel --quiet
    pip install -r requirements.txt --quiet || {
        log_error "pip install failed"
        exit 1
    }

    log_success "Dependencies up to date"
}

# =============================================================================
# Step 4 — Run migrations
# =============================================================================

run_migrations() {
    log_section "Step 4: Running Migrations"

    python manage.py migrate --noinput || {
        log_error "Migrations failed"
        exit 1
    }

    log_success "Migrations completed"
}

# =============================================================================
# Step 5 — Run tests (skipped if no tests exist)
# =============================================================================

run_tests() {
    log_section "Step 5: Running Tests"

    # Count test files across all apps — skip step if none exist yet
    TEST_COUNT=$(find . -name "tests*.py" -not -path "./.git/*" | wc -l)

    if [ "$TEST_COUNT" -eq 0 ]; then
        log_warning "No test files found — skipping (add tests/*.py to any app to enable)"
        return 0
    fi

    log_info "Found $TEST_COUNT test file(s) — running suite..."

    # Capture output and exit code correctly (assignment always exits 0 in bash)
    TEST_OUTPUT=$(python manage.py test --noinput 2>&1; echo "__EXIT__$?")
    TEST_EXIT=$(echo "$TEST_OUTPUT" | sed -n 's/.*__EXIT__//p')
    TEST_OUTPUT=$(echo "$TEST_OUTPUT" | sed 's/__EXIT__[0-9]*//')

    if [ "$TEST_EXIT" != "0" ]; then
        log_error "Tests FAILED — aborting deployment (Gunicorn still running old code)"
        echo ""
        echo "─────────────────────────────────────────────────"
        echo "$TEST_OUTPUT"
        echo "─────────────────────────────────────────────────"
        echo ""
        log_info "Fix the failures, then run ./redeploy.sh again."
        exit 1
    fi

    log_success "All tests passed"
}

# =============================================================================
# Step 6 — Collect static files
# =============================================================================

collect_static() {
    log_section "Step 6: Collecting Static Files"

    python manage.py collectstatic --noinput --clear || {
        log_error "collectstatic failed"
        exit 1
    }

    log_success "Static files collected"
}

# =============================================================================
# Step 7 — Restart Gunicorn
# =============================================================================

restart_service() {
    log_section "Step 7: Restarting Gunicorn"

    # Clear Python bytecode cache so stale .pyc files don't survive the restart
    log_info "Clearing bytecode cache..."
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
    log_success "Bytecode cache cleared"

    OLD_PID=""
    if systemctl is-active --quiet "$GUNICORN_SERVICE_NAME"; then
        OLD_PID=$(systemctl show -p MainPID "$GUNICORN_SERVICE_NAME" | cut -d= -f2)
    fi

    sudo systemctl restart "$GUNICORN_SERVICE_NAME"
    sleep 3

    if ! systemctl is-active --quiet "$GUNICORN_SERVICE_NAME"; then
        log_error "Gunicorn failed to restart"
        log_info "  sudo journalctl -u $GUNICORN_SERVICE_NAME -n 50"
        exit 1
    fi

    NEW_PID=$(systemctl show -p MainPID "$GUNICORN_SERVICE_NAME" | cut -d= -f2)

    if [ -n "$OLD_PID" ] && [ "$OLD_PID" = "$NEW_PID" ]; then
        log_warning "PID unchanged ($NEW_PID) — service may not have fully restarted"
        log_info "Check: sudo journalctl -u $GUNICORN_SERVICE_NAME -n 20"
    else
        log_success "Gunicorn restarted (PID $OLD_PID → $NEW_PID)"
    fi

    log_info "Reloading Nginx..."
    sudo systemctl reload nginx
    log_success "Nginx reloaded"
}

# =============================================================================
# Main
# =============================================================================

main() {
    log_section "Islan.DEV Redeploy Starting"
    log_info "Environment : $DJANGO_ENV"
    log_info "Settings    : $DJANGO_SETTINGS_MODULE"
    log_info "Service     : $GUNICORN_SERVICE_NAME"
    log_info "Project root: $PROJECT_ROOT"
    echo ""

    validate_service
    pull_code
    activate_venv
    install_deps
    run_migrations
    run_tests
    collect_static
    restart_service

    log_section "✅ Redeploy Completed Successfully"
    log_success "$(date)"
    echo ""
}

main
