#!/usr/bin/env bash
set -euo pipefail

cat docker/settings_local.template.py | envsubst > re2o/settings_local.py

AUTOMIGRATE=${AUTOMIGRATE:-yes}

if [ "$AUTOMIGRATE" != "skip" ]; then
  python3 manage.py migrate --noinput
fi

cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.filter(pseudo='$SUPERUSER_LOGIN').exists() or \
    User.objects.create_superuser(pseudo='$SUPERUSER_LOGIN', email='$SUPERUSER_EMAIL', password='$SUPERUSER_PASS', surname='$SUPERUSER_LOGIN')
EOF
python manage.py runserver 0.0.0.0:8000