#!/bin/sh

# Wait for postgres to be ready
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

# Initialize Flask-Migrate if not already done
if [ ! -d "/app/migrations/versions" ] || [ -z "$(ls -A /app/migrations/versions)" ]; then
    echo "Initializing database migrations..."
    flask db init || echo "Migrations already initialized"
    flask db migrate -m "Initial migration"
fi

# Run migrations
echo "Running database migrations..."
flask db upgrade

# Initialize roles if not present
echo "Initializing roles..."
flask shell << 'PYEOF'
from app.models import Role, User
from app import db
try:
    Role.insert_roles()
    print("✓ Roles initialized")
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_role = Role.query.filter_by(name='Administrator').first()
        admin = User(
            email='admin@example.com',
            username='admin',
            password='admin123',
            confirmed=True,
            role=admin_role
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
except Exception as e:
    print(f"Note: {e}")
exit()
PYEOF

echo "Starting Flask application..."
flask run --host=0.0.0.0 -p $FLASK_PORT