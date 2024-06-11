#!/bin/sh

# Wait for the PostgreSQL server to be available
echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL started"

# Apply Django migrations
echo "Applying Django migrations..."
python manage.py migrate

# Start your Django application
exec "$@"