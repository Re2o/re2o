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
"""Fonction de context, variables renvoyées à toutes les vues"""


from __future__ import unicode_literals
from django.contrib import messages

from preferences.models import GeneralOption, OptionalMachine


def context_user(request):
    """Fonction de context lorsqu'un user est logué (ou non),
    renvoie les infos sur l'user, la liste de ses droits, ses machines"""
    general_options, _created = GeneralOption.objects.get_or_create()
    machine_options, _created = OptionalMachine.objects.get_or_create()
    user = request.user
    global_message = general_options.general_message
    if global_message:
        messages.warning(request, global_message)
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    return {
        'request_user': user,
        'interfaces': interfaces,
        'site_name': general_options.site_name,
        'ipv6_enabled': machine_options.ipv6,
    }
