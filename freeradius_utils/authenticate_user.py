import os, sys

proj_path = "/var/www/re2o/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import argparse

from django.contrib.auth import authenticate
from users.models import User


def authorize_user(user, password):
    user = authenticate(username=user, password=password) 
    if user:
        if User.objects.get(pseudo=user):
            return "TRUE"
        else:
            return "FALSE"
    else:
        return "FALSE"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Authorize user')
    parser.add_argument('user', action="store")
    parser.add_argument('password', action="store")
    args = parser.parse_args()
    print(authorize_user(args.user, args.password))

