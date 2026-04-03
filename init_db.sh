#!/bin/bash

echo "=== Database Initialization Script ==="
echo

# Start services if not running
echo "Starting services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres rabbit mediamtx

# Wait for postgres
echo "Waiting for PostgreSQL..."
sleep 10

# Run database initialization
echo "Initializing database..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm web sh -c "
flask db init || true
flask db migrate -m 'Initial migration' || true  
flask db upgrade

python << 'PYEOF'
from app import create_app, db
from app.models import Role, User
import os

app = create_app('development')
with app.app_context():
    # Insert roles
    Role.insert_roles()
    print('✓ Roles created')
    
    # Create admin
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
        print('✓ Admin user created: admin / admin')
    else:
        # Update to admin role and password
        admin.role = Role.query.filter_by(name='Administrator').first()
        admin.password = 'admin'
        db.session.commit()
        print('✓ Admin user updated: admin / admin')
PYEOF
"

echo
echo "=== Database initialized! ==="
echo "Now start all services with:"
echo "docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
echo
echo "Login credentials:"
echo "  Username: admin"
echo "  Password: admin"
