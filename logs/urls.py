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
"""logs.urls
The defined URLs for the logs app. Included in re2o.urls.
"""
from __future__ import unicode_literals

from django.urls import path

from . import views

app_name = "logs"

urlpatterns = [
    path("", views.index, name="index"),
    path("stats_logs", views.stats_logs, name="stats-logs"),
    path(
        "revert_action/<int:revision_id>",
        views.revert_action,
        name="revert-action",
    ),
    path(
        "<str:application>/<str:object_name>/<int:object_id>",
        views.history,
        name="history",
    ),
    path("stats_general", views.stats_general, name="stats-general"),
    path("stats_models", views.stats_models, name="stats-models"),
    path("stats_users", views.stats_users, name="stats-users"),
    path("stats_actions", views.stats_actions, name="stats-actions"),
    path("stats_search_machine", views.stats_search_machine_history, name="stats-search-machine"),
]
