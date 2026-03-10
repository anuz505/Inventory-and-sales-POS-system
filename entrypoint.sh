#!/bin/sh
# set -e
echo "applying migrations"
python manage.py migrate

echo "populating db"
python manage.py populate_db

echo "starting server"
echo "Starting server..."
exec gunicorn internship_task.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -