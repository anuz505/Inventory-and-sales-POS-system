#!/bin/sh
set -e
echo "applying migartions"
python manage.py makemigrations
python manage.py migrate

echo "populating db"
python manage.py populate_db

echo "starting server"
python manage.py runserver 0.0.0.0:8000