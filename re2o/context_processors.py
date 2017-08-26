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
from preferences.models import GeneralOption

def context_user(request):
    general_options, created = GeneralOption.objects.get_or_create()
    user = request.user
    if user.is_authenticated():
        interfaces = user.user_interfaces()
        is_cableur = user.is_cableur
        is_bureau = user.is_bureau
        is_bofh = user.is_bofh
        is_trez = user.is_trez
        is_infra = user.is_infra
        is_admin = user.is_admin
    else:
        interfaces = None
        is_cableur = False
        is_bureau = False
        is_bofh = False
        is_trez = False
        is_infra = False
        is_admin = False
    return {
        'request_user': user,
        'is_cableur': is_cableur,
        'is_bureau': is_bureau,
        'is_bofh': is_bofh,
        'is_trez': is_trez,
        'is_infra': is_infra,
        'is_admin' : is_admin,
        'interfaces': interfaces,
        'site_name': general_options.site_name,
    }
