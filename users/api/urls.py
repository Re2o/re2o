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

"""Defines the URLs of the API User

A custom router is used to register all the routes. That allows to register
all the URL patterns from the viewsets as a standard router but, the views
can also be register. That way a complete API root page presenting all URLs
can be generated automatically.
"""

from django.conf.urls import url, include

from . import views
from api.routers import AllViewsRouter

def add_to_router(router):
    router.register_viewset(r'users/user', views.UserViewSet, base_name='user')
    router.register_viewset(r'users/homecreation', views.HomeCreationViewSet, base_name='homecreation')
    router.register_viewset(r'users/normaluser', views.NormalUserViewSet, base_name='normaluser')
    router.register_viewset(r'users/criticaluser', views.CriticalUserViewSet, base_name='criticaluser')
    router.register_viewset(r'users/club', views.ClubViewSet)
    router.register_viewset(r'users/adherent', views.AdherentViewSet)
    router.register_viewset(r'users/serviceuser', views.ServiceUserViewSet)
    router.register_viewset(r'users/school', views.SchoolViewSet)
    router.register_viewset(r'users/listright', views.ListRightViewSet)
    router.register_viewset(r'users/shell', views.ShellViewSet, base_name='shell')
    router.register_viewset(r'users/ban', views.BanViewSet)
    router.register_viewset(r'users/whitelist', views.WhitelistViewSet)
    router.register_viewset(r'users/emailaddress', views.EMailAddressViewSet)
