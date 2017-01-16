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

from machines.models import Interface, Machine
from .settings import SITE_NAME

def context_user(request):
    user = request.user
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    is_cableur = user.has_perms(('cableur',))
    is_bureau = user.has_perms(('bureau',))
    is_bofh = user.has_perms(('bofh',))
    is_trez = user.has_perms(('trésorier',))
    is_infra = user.has_perms(('infra',))
    return {
        'request_user': user,
        'is_cableur': is_cableur,
        'is_bureau': is_bureau,
        'is_bofh': is_bofh,
        'is_trez': is_trez,
        'is_infra': is_infra,
        'interfaces': interfaces,
        'site_name': SITE_NAME,
    }
