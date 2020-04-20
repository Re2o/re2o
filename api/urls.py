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

from django.conf.urls import url, include

from . import views
from .routers import AllViewsRouter
from cotisations.api.urls import urls_viewset as urls_viewset_cotisations
from cotisations.api.urls import urls_view as urls_view_cotisations
from machines.api.urls import urls_viewset as urls_viewset_machines
from machines.api.urls import urls_view as urls_view_machines
from preferences.api.urls import urls_viewset as urls_viewset_preferences
from preferences.api.urls import urls_view as urls_view_preferences
from topologie.api.urls import urls_viewset as urls_viewset_topologie
from topologie.api.urls import urls_view as urls_view_topologie
from users.api.urls import urls_viewset as urls_viewset_users
from users.api.urls import urls_view as urls_view_users

urls_viewset = urls_viewset_cotisations + urls_viewset_machines + urls_viewset_preferences + urls_viewset_topologie + urls_viewset_users
urls_view = urls_view_cotisations + urls_view_machines + urls_view_preferences + urls_view_topologie + urls_view_users

router = AllViewsRouter()


for _url, viewset, name in urls_viewset:
    if name == None:
        router.register_viewset(_url, viewset)
    else:
        router.register_viewset(_url, viewset, basename=name)

for _url, view in urls_view:
    router.register_view(_url, view)

# Reminder
router.register_view(r"reminder/get-users", views.ReminderView),
# TOKEN AUTHENTICATION
router.register_view(r"token-auth", views.ObtainExpiringAuthToken)

urlpatterns = [url(r"^", include(router.urls))]
