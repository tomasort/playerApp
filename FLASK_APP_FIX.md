# Flask App Fix - FLASK_APP Environment Variable

## Issue
Flask application was failing to start with error:
```
Error: Detected factory 'create_app' in module 'app', but could not call it without arguments.
```

This caused all Flask CLI commands (`flask db`, `flask shell`, etc.) to fail, preventing database migrations and initialization.

## Root Cause
The application uses a factory pattern with `create_app()` function in `app/__init__.py`, but Flask didn't know which module to load. The FLASK_APP environment variable was not set, causing Flask to look for a simple `app` instance instead of calling `create_app()`.

## Solution
Added `FLASK_APP=playerApp.py` to the common environment variables in docker-compose.yml.

### Changes Made

**File: docker-compose.yml**
```yaml
x-common-env: &common-env
  FLASK_APP: playerApp.py  # <-- Added this line
  FLASK_CONFIG: production
  DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
  ...
```

## Result
✅ Flask application now starts successfully
✅ Database migrations run automatically on startup
✅ Roles and admin user created properly
✅ All Flask CLI commands work correctly
✅ API endpoints responding (e.g., /stream/status returns JSON)

## Verification
```bash
# Test status endpoint
curl http://localhost/stream/status
# Expected output: {"is_running":false,"session_id":null,"started_at":null,"started_by":null}

# Check container status
docker ps
# All 7 services should be running
```

## playerApp.py Structure
The `playerApp.py` file at the root of StreamerApp/ contains:
- `app = create_app(os.getenv('FLASK_CONFIG') or 'default')` - Creates app instance
- `migrate = Migrate(app, db)` - Initializes Flask-Migrate
- Shell context processor for database access
- CLI commands for testing

This file serves as the entry point for Flask CLI and Gunicorn.
