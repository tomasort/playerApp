# Automated Database Initialization

## Problem Solved
The database tables weren't being created automatically on first run, causing errors like:
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

## Solution
Updated startup scripts to automatically:
1. **Wait for PostgreSQL** to be ready
2. **Initialize Flask-Migrate** if not already done
3. **Run database migrations** automatically
4. **Create roles** (Watcher, User, Administrator)
5. **Create admin user** if it doesn't exist

## What Was Changed

### Files Updated:
1. `StreamerApp/docker/local/start.sh` - Development startup
2. `StreamerApp/docker/prod/start.sh` - Production startup  
3. `StreamerApp/docker/local/Dockerfile` - Added netcat-openbsd
4. `StreamerApp/docker/prod/Dockerfile` - Added netcat-openbsd

### New Startup Flow:
```bash
1. Wait for PostgreSQL to be available
2. Check if migrations directory exists
   - If not: Run `flask db init` and `flask db migrate`
3. Run `flask db upgrade` to apply migrations
4. Initialize roles using Role.insert_roles()
5. Create admin user if doesn't exist
   - Username: admin
   - Password: admin123
   - Role: Administrator
6. Start Flask application
```

## Benefits

✅ **No Manual Setup**: Database initializes automatically on first run
✅ **Idempotent**: Safe to run multiple times, won't duplicate data
✅ **Fresh Starts**: `docker-compose down -v` creates clean database automatically
✅ **Production Ready**: Works in both dev and production environments
✅ **User Friendly**: Admin user created automatically

## Testing

### Test Fresh Database:
```bash
# Remove all data
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

# Start fresh (database will auto-initialize)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Watch the logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs web
```

You should see:
```
Waiting for postgres...
PostgreSQL started
Initializing database migrations...
Running database migrations...
Initializing roles...
✓ Roles initialized
✓ Admin user created (username: admin, password: admin123)
Starting Flask application...
```

### Verify Database:
```bash
# Check tables exist
docker-compose exec postgres psql -U username -d db -c "\dt"

# Check admin user
docker-compose exec web flask shell
>>> from app.models import User
>>> User.query.filter_by(username='admin').first()
>>> exit()
```

## How It Works

### PostgreSQL Wait Loop:
```bash
while ! nc -z postgres 5432; do
  sleep 0.5
done
```
Uses netcat to check if PostgreSQL port 5432 is accepting connections.

### Migration Check:
```bash
if [ ! -d "/app/migrations/versions" ] || [ -z "$(ls -A /app/migrations/versions)" ]; then
    flask db init
    flask db migrate -m "Initial migration"
fi
```
Only initializes if migrations directory is empty.

### Role & User Creation:
```python
Role.insert_roles()  # Creates Watcher, User, Administrator roles
# Creates admin user with Administrator role if doesn't exist
```

## Troubleshooting

### If database initialization fails:

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose ps postgres
   ```

2. **Check web service logs:**
   ```bash
   docker-compose logs web
   ```

3. **Manual initialization (if needed):**
   ```bash
   docker-compose exec web flask db init
   docker-compose exec web flask db migrate -m "Initial"
   docker-compose exec web flask db upgrade
   ```

4. **Reset everything:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

## Environment Variables

The startup script respects these environment variables:
- `FLASK_PORT` - Port for Flask to run on
- `DATABASE_URL` or `DEV_DATABASE_URL` - PostgreSQL connection string
- Environment automatically set by docker-compose

## Admin User

Default admin credentials (automatically created):
- **Username**: `admin`
- **Email**: `admin@example.com`  
- **Password**: `admin123`
- **Role**: Administrator
- **Permissions**: All (Watch, Stream Control, Admin)

**⚠️ IMPORTANT**: Change the admin password after first login in production!

```python
# Change password via Flask shell:
docker-compose exec web flask shell
>>> from app.models import User
>>> from app import db
>>> admin = User.query.filter_by(username='admin').first()
>>> admin.password = 'your-new-secure-password'
>>> db.session.commit()
>>> exit()
```

## Summary

Now you can simply run:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

And everything will be automatically initialized on first run! 🎉
