# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
