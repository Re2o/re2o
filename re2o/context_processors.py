# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
"""Context functions, runs and results sends globaly to all templates"""

from __future__ import unicode_literals

import datetime

from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpRequest
from preferences.models import GeneralOption, OptionalMachine
from django.utils.translation import get_language
from importlib import import_module
from re2o.settings_local import OPTIONNAL_APPS_RE2O


def context_user(request):
    """Global Context function

        Returns:
        dict:Containing user's interfaces and himself if logged, else None

    """
    user = request.user
    if get_language() == "fr":
        global_message = GeneralOption.get_cached_value("general_message_fr")
    else:
        global_message = GeneralOption.get_cached_value("general_message_en")
    if global_message:
        if isinstance(request, HttpRequest):
            if global_message not in [msg.message for msg in get_messages(request)]:
                messages.warning(request, global_message)
        else:
            if global_message not in [msg.message for msg in get_messages(request._request)]:
                messages.warning(request._request, global_message)
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    return {
        "request_user": user,
        "interfaces": interfaces,
        # Must takes a different name because djang.auth.contrib.views.login()
        # overrides 'site_name' context variable.
        "name_website": GeneralOption.get_cached_value("site_name"),
        "ipv6_enabled": OptionalMachine.get_cached_value("ipv6"),
    }


def context_optionnal_apps(request):
    """Context functions. Called to add optionnal apps buttons in navbari

        Returns:
        dict:Containing optionnal template list of functions for navbar found
        in optional apps

    """
    optionnal_apps = [import_module(app) for app in OPTIONNAL_APPS_RE2O]
    optionnal_templates_navbar_user_list = [
        app.views.navbar_user()
        for app in optionnal_apps
        if hasattr(app.views, "navbar_user")
    ]
    optionnal_templates_navbar_logout_list = [
        app.views.navbar_logout()
        for app in optionnal_apps
        if hasattr(app.views, "navbar_logout")
    ]
    return {
        "optionnal_templates_navbar_user_list": optionnal_templates_navbar_user_list,
        "optionnal_templates_navbar_logout_list": optionnal_templates_navbar_logout_list,
    }


def date_now(request):
    """Add the current date in the context for quick informations and
    comparisons"""
    return {
        "now_aware": datetime.datetime.now(datetime.timezone.utc),
        "now_naive": datetime.datetime.now(),
    }
