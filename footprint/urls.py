# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Jean-Romain Garnier
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
Footprint optional app urls
"""

from django.urls import path, re_path

from . import views
from .preferences.views import edit_options

app_name = "footprint"

urlpatterns = [
    re_path(
        r"^edit_options/(?P<section>FootprintOption)$",
        edit_options,
        name="edit-options",
    ),
    path(
        "data_usage_estimate/<int:userid>",
        views.get_data_usage_estimate,
        name="data-usage-estimate",
    ),
]
