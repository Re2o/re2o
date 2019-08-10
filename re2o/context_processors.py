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

import datetime

from django.contrib import messages
from django.http import HttpRequest
from preferences.models import GeneralOption, OptionalMachine
from django.utils.translation import get_language
from importlib import import_module
from re2o.settings_local import OPTIONNAL_APPS

def context_user(request):
    """Fonction de context lorsqu'un user est logué (ou non),
    renvoie les infos sur l'user, la liste de ses droits, ses machines"""
    user = request.user
    if get_language()=='fr':
        global_message = GeneralOption.get_cached_value('general_message_fr')
    else:
        global_message = GeneralOption.get_cached_value('general_message_en')
    if global_message:
        if isinstance(request, HttpRequest):
            messages.warning(request, global_message)
        else:
            messages.warning(request._request, global_message)
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    return {
        'request_user': user,
        'interfaces': interfaces,
        # Must takes a different name because djang.auth.contrib.views.login()
        # overrides 'site_name' context variable.
        'name_website': GeneralOption.get_cached_value('site_name'),
        'ipv6_enabled': OptionalMachine.get_cached_value('ipv6'),
    }

def context_optionnal_apps(request):
    """Fonction de context pour générer la navbar en fonction des
    apps optionnels"""
    optionnal_apps = [import_module(app) for app in OPTIONNAL_APPS]
    optionnal_templates_navbar_list = [app.views.navbar(request) for app in optionnal_apps]
    return {'optionnal_templates_navbar_list':optionnal_templates_navbar_list}


def date_now(request):
    """Add the current date in the context for quick informations and
    comparisons"""
    return {
        'now_aware': datetime.datetime.now(datetime.timezone.utc),
        'now_naive': datetime.datetime.now()
    }
