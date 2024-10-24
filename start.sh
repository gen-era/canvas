#!/bin/bash

# Run migrate
echo "Running migrations..."
python manage.py migrate --run-syncdb

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn \
    cnvapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --log-level debug \
    --access-logfile '-' \
    --error-logfile '-' \
    --worker-class gevent \
    --workers 2
