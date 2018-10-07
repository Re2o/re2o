#!/bin/sh

# Migrate database
python manage.py migrate --noinput

# Collect statics
python manage.py collectstatic --noinput

exec "$@"

