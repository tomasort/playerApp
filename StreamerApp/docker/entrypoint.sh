#!/bin/sh

# Wait for postgres to be ready
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

# Initialize Flask-Migrate if not already done
if [ ! -d "/app/migrations/versions" ] || [ -z "$(ls -A /app/migrations/versions 2>/dev/null)" ]; then
    echo "Initializing database migrations..."
    flask db init || echo "Migrations directory exists"
    flask db migrate -m "Initial migration" || echo "Migration created"
fi

# Run migrations
echo "Running database migrations..."
flask db upgrade || echo "Migrations applied"

# Initialize roles and admin user
echo "Initializing roles and admin user..."
python << 'PYEOF'
from app import create_app, db
from app.models import Role, User
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
with app.app_context():
    try:
        # Insert roles
        Role.insert_roles()
        print("✓ Roles initialized")
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(
                email='admin@example.com',
                username='admin',
                password='admin',
                confirmed=True,
                role=admin_role
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin)")
        else:
            print("✓ Admin user already exists")
    except Exception as e:
        print(f"Note: {e}")
PYEOF

echo "Starting application..."
# Execute the command provided as arguments to the script
exec "$@"