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
Deposits url
"""

from django.urls import path

from . import views

app_name = "deposits"

urlpatterns = [
    path("new_deposit/<int:userid>", views.new_deposit, name="new-deposit"),
    path("edit_deposit/<int:depositid>", views.edit_deposit, name="edit-deposit"),
    path("del_deposit/<int:depositid>", views.del_deposit, name="del-deposit"),
    path("index_deposits", views.index_deposits, name="index-deposits"),
    path("add_deposit_item", views.add_deposit_item, name="add-deposit-item"),
    path(
        "edit_deposit_item/<int:itemid>",
        views.edit_deposit_item,
        name="edit-deposit-item",
    ),
    path("del_deposit_item", views.del_deposit_item, name="del-deposit-item"),
    path("index_deposit_item", views.index_deposit_item, name="index-deposit-item"),
    path("index_stats", views.index_stats, name="index-stats"),
]
