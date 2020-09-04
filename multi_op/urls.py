# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Gabriel Détraz
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
"""
The database models for the 'urls' app of re2o.

For further details on each of those models, see the documentation details for
each.
"""

from django.conf.urls import url

from . import views
from .preferences.views import edit_options

urlpatterns = [
    url(r"^$", views.aff_state_global, name="aff-state-global"),
    url(
        r"^(?P<dormitoryid>[0-9]+)$",
        views.aff_state_dormitory,
        name="aff-state-dormitory",
    ),
    url(
        r"^edit_options/(?P<section>MultiopOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^pending-connection$",
        views.aff_pending_connection,
        name="aff-pending-connection",
    ),
    url(
        r"^pending-disconnection$",
        views.aff_pending_disconnection,
        name="aff-pending-disconnection",
    ),
    url(
        r"^disconnect-room/(?P<roomid>[0-9]+)$",
        views.disconnect_room,
        name="disconnect-room",
    ),
]
