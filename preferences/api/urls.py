# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019 Arthur Grisel-Davy
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

from django.conf.urls import url, include

from . import views
from api.routers import AllViewsRouter

def add_to_router(router):
    router.register_view(r'preferences/optionaluser', views.OptionalUserView),
    router.register_view(r'preferences/optionalmachine', views.OptionalMachineView),
    router.register_view(r'preferences/optionaltopologie', views.OptionalTopologieView),
    router.register_view(r'preferences/radiusoption', views.RadiusOptionView),
    router.register_view(r'preferences/generaloption', views.GeneralOptionView),
    router.register_viewset(r'preferences/service', views.HomeServiceViewSet, base_name='homeservice'),
    router.register_view(r'preferences/assooption', views.AssoOptionView),
    router.register_view(r'preferences/homeoption', views.HomeOptionView),
    router.register_view(r'preferences/mailmessageoption', views.MailMessageOptionView),
