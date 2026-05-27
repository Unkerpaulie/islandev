# Islan.DEV

The public marketing site for Islan.DEV Digital Solutions — a one-person digital transformation practice for small and medium enterprises. Built as a content-managed Django application with a small set of inbound-lead models and a portfolio backed by the admin.

## Tech stack

- Python 3.12, Django 5.2
- PostgreSQL (prod), SQLite (dev)
- Gunicorn behind a reverse proxy (Ubuntu VPS)
- WhiteNoise for static file serving
- Tailwind CSS (standalone CLI) for styling, Inter font via Google Fonts

## Local development

This project assumes the shared `djvenv` lives outside all repos (per project conventions). From the repo root:

```bash
# Activate the shared venv (Windows)
..\..\djvenv\Scripts\activate

# Or (Unix-like)
source ../../djvenv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000.

### Building CSS

This project uses the Tailwind standalone CLI (no Node.js required). Download the binary for your platform from https://github.com/tailwindlabs/tailwindcss/releases/latest and drop it next to the project (or anywhere on your PATH). The binary is gitignored.

Then build the stylesheet:

```bash
# One-off build
./tailwindcss -i static/src/input.css -o static/css/site.css --minify

# Watch mode during development
./tailwindcss -i static/src/input.css -o static/css/site.css --watch
```

## Environment variables

The application reads all configuration from `<islandev_root>/.env` — one level above this repo. The committed `.env.example` documents every variable with a placeholder value. The populated `.env` is never committed.

Both deploy scripts and the production systemd unit file source the same `.env`, including `DJANGO_SETTINGS_MODULE`. Changing the active settings module never requires editing a unit file.

## Deployment

Two manual scripts at the repo root form the deploy pipeline:

- `build.sh` — first-time deploy. Creates the venv, installs deps, migrates, collects static files, restarts Gunicorn.
- `redeploy.sh` — every subsequent deploy. Pulls `main`, syncs deps, migrates, **runs the full test suite (failure aborts the deploy)**, collects static files, restarts Gunicorn.

The active branch is always `main`.

## Running tests

```bash
python manage.py test
```

Tests use Django's built-in `TestCase`. Each app has its own `tests.py`.

## Apps

- `core` — root URL routing, the home page, the services page, and shared utilities.
- `engagement` — three lead-capture models: `BookingRequest` (consultation bookings), `ContactInquiry` (client and collaborator contact submissions), `Subscriber` (newsletter signups).
- `portfolio` — `Project` and `ProjectImage` models for case-study entries with admin-managed screenshots.
