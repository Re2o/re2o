"""
WSGI config for re2o project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from os.path import dirname
import sys

sys.path.append(dirname(dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")

application = get_wsgi_application()
