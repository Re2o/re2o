# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

"""Defines the URLs of the API

A custom router is used to register all the routes. That allows to register
all the URL patterns from the viewsets as a standard router but, the views
can also be register. That way a complete API root page presenting all URLs
can be generated automatically.
"""

import importlib

from django.conf import settings
from django.conf.urls import url, include

from . import views
from .routers import AllViewsRouter

router = AllViewsRouter()

for app in settings.INSTALLED_APPS:
    try:
        module = importlib.import_module(app + '.api.urls')
        add_to_router = getattr(module, 'add_to_router')
        add_to_router(router)
    except ImportError:
        pass


# SERVICE REGEN
router.register_viewset(r'services/regen', views.ServiceRegenViewSet, base_name='serviceregen')
# DHCP
router.register_view(r'dhcp/hostmacip', views.HostMacIpView),
# LOCAL EMAILS
router.register_view(r'localemail/users', views.LocalEmailUsersView),
# Firewall
router.register_view(r'firewall/subnet-ports', views.SubnetPortsOpenView),
router.register_view(r'firewall/interface-ports', views.InterfacePortsOpenView),
# Switches config
router.register_view(r'switchs/ports-config', views.SwitchPortView),
router.register_view(r'switchs/role', views.RoleView),
# Reminder
router.register_view(r'reminder/get-users', views.ReminderView),
# DNS
router.register_view(r'dns/zones', views.DNSZonesView),
router.register_view(r'dns/reverse-zones', views.DNSReverseZonesView),
# MAILING
router.register_view(r'mailing/standard', views.StandardMailingView),
router.register_view(r'mailing/club', views.ClubMailingView),
# TOKEN AUTHENTICATION
router.register_view(r'token-auth', views.ObtainExpiringAuthToken)

urlpatterns = [
    url(r'^', include(router.urls)),
]
