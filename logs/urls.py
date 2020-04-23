# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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
"""
Urls de l'application logs, pointe vers les fonctions de views.
Inclu dans le re2o.urls
"""
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^stats_logs$", views.stats_logs, name="stats-logs"),
    url(
        r"^revert_action/(?P<revision_id>[0-9]+)$",
        views.revert_action,
        name="revert-action",
    ),
    url(
        r"(?P<application>\w+)/(?P<object_name>\w+)/(?P<object_id>[0-9]+)$",
        views.history,
        name="history",
    ),
    url(
        r"(?P<object_name>\w+)/(?P<object_id>[0-9]+)$",
        views.detailed_history,
        name="detailed-history",
    ),
    url(r"^stats_general/$", views.stats_general, name="stats-general"),
    url(r"^stats_models/$", views.stats_models, name="stats-models"),
    url(r"^stats_users/$", views.stats_users, name="stats-users"),
    url(r"^stats_actions/$", views.stats_actions, name="stats-actions"),
    url(r"^stats_search_machine/$", views.stats_search_machine_history, name="stats-search-machine"),
]
