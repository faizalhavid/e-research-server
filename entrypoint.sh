#!/bin/sh

# Use the DB_HOST environment variable to wait for the PostgreSQL server to be available
echo "Waiting for PostgreSQL to start..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"

# Apply Django migrations
echo "Applying Django migrations..."
python manage.py migrate

# Start your Django application
exec "$@"