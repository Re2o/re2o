### Appellé par cron, mets à jour la base de donnée ldap, par défaut le dialup access
### Argument full, mets tout à jour

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

from users.models import User

def refresh_ldap(base=False, access_refresh=True, mac_refresh=False):
    for u in User.objects.all():
        u.ldap_sync(base=base, access_refresh=access_refresh, mac_refresh=mac_refresh)
    return

if __name__ == '__main__':
    if "base" in sys.argv:
        refresh_ldap(base=True, access_refresh=True, mac_refresh=False)
    elif "full" in sys.argv:
        refresh_ldap(base=True, access_refresh=True, mac_refresh=True)
    else:
        refresh_ldap()
