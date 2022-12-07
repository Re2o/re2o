# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
# Copyright © 2020 Caroline Canebier
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

from importlib import import_module

from django.conf import settings
from django.urls import include, path

from . import views
from .routers import AllViewsRouter

app_name = "api"

router = AllViewsRouter()

urls_viewset = []
urls_view = []
urls_functional_view = []

for app in settings.INSTALLED_APPS:
    try:
        module = import_module(".api.urls", package=app)
        urls_viewset += getattr(module, "urls_viewset", [])
        urls_view += getattr(module, "urls_view", [])
        urls_functional_view += getattr(module, "urls_functional_view", [])
    except ImportError:
        continue

for _url, viewset, name in urls_viewset:
    if name == None:
        router.register_viewset(_url, viewset)
    else:
        router.register_viewset(_url, viewset, basename=name)

for _url, view in urls_view:
    router.register_view(_url, view)

for _url, view, name in urls_functional_view:
    router.register_functional_view(_url, view, name)

# TOKEN AUTHENTICATION
router.register_view(r"token-auth", views.ObtainExpiringAuthToken)

urlpatterns = [path("", include(router.urls))]
