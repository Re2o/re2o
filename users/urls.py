# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017-2020  Gabriel Détraz
# Copyright © 2017-2020  Lara Kermarec
# Copyright © 2017-2020  Augustin Lemesle
# Copyright © 2017-2020  Hugo Levy--Falk
# Copyright © 2017-2020  Jean-Romain Garnier
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
The defined URLs for the Users app
"""

from __future__ import unicode_literals

from django.urls import path, re_path

from . import views, views_autocomplete

app_name = "users"

urlpatterns = [
    path("new_user", views.new_user, name="new-user"),
    path("new_club", views.new_club, name="new-club"),
    path("edit_info/<int:userid>", views.edit_info, name="edit-info"),
    path(
        "edit_club_admin_members/<int:clubid>",
        views.edit_club_admin_members,
        name="edit-club-admin-members",
    ),
    path("state/<int:userid>", views.state, name="state"),
    path("groups/<int:userid>", views.groups, name="groups"),
    path("password/<int:userid>", views.password, name="password"),
    path(
        "confirm_email/<int:userid>",
        views.resend_confirmation_email,
        name="resend-confirmation-email",
    ),
    path(
        "del_group/<int:userid>/<int:listrightid>",
        views.del_group,
        name="del-group",
    ),
    path("del_superuser/<int:userid>", views.del_superuser, name="del-superuser"),
    path("new_serviceuser", views.new_serviceuser, name="new-serviceuser"),
    path(
        "edit_serviceuser/<int:serviceuserid>",
        views.edit_serviceuser,
        name="edit-serviceuser",
    ),
    path(
        "del_serviceuser/<int:serviceuserid>",
        views.del_serviceuser,
        name="del-serviceuser",
    ),
    path("add_ban/<int:userid>", views.add_ban, name="add-ban"),
    path("edit_ban/<int:banid>", views.edit_ban, name="edit-ban"),
    path("del-ban/<int:banid>", views.del_ban, name="del-ban"),
    path("add_whitelist/<int:userid>", views.add_whitelist, name="add-whitelist"),
    path(
        "edit_whitelist/<int:whitelistid>",
        views.edit_whitelist,
        name="edit-whitelist",
    ),
    path(
        "del_whitelist/<int:whitelistid>",
        views.del_whitelist,
        name="del-whitelist",
    ),
    path(
        "add_emailaddress/<int:userid>",
        views.add_emailaddress,
        name="add-emailaddress",
    ),
    path(
        "edit_emailaddress/<int:emailaddressid>",
        views.edit_emailaddress,
        name="edit-emailaddress",
    ),
    path(
        "del_emailaddress/<int:emailaddressid>",
        views.del_emailaddress,
        name="del-emailaddress",
    ),
    path(
        "edit_email_settings/<int:userid>",
        views.edit_email_settings,
        name="edit-email-settings",
    ),
    path("add_school", views.add_school, name="add-school"),
    path("edit_school/<int:schoolid>", views.edit_school, name="edit-school"),
    path("del_school", views.del_school, name="del-school"),
    path("add_listright", views.add_listright, name="add-listright"),
    path(
        "edit_listright/<int:listrightid>",
        views.edit_listright,
        name="edit-listright",
    ),
    path("del_listright", views.del_listright, name="del-listright"),
    path("add_shell", views.add_shell, name="add-shell"),
    path("edit_shell/<int:listshellid>", views.edit_shell, name="edit-shell"),
    path("del_shell/<int:listshellid>", views.del_shell, name="del-shell"),
    path("profil/<int:userid>", views.profil, name="profil"),
    path("index_ban", views.index_ban, name="index-ban"),
    path("index_white", views.index_white, name="index-white"),
    path("index_school", views.index_school, name="index-school"),
    path("index_shell", views.index_shell, name="index-shell"),
    path("index_listright", views.index_listright, name="index-listright"),
    path("index_serviceusers", views.index_serviceusers, name="index-serviceusers"),
    path("mon_profil", views.mon_profil, name="mon-profil"),
    re_path(r"^process/(?P<token>[a-z0-9]{32})/$", views.process, name="process"),
    path("reset_password", views.reset_password, name="reset-password"),
    path("mass_archive", views.mass_archive, name="mass-archive"),
    path("", views.index, name="index"),
    path("index_clubs", views.index_clubs, name="index-clubs"),
    path("initial_register", views.initial_register, name="initial-register"),
    path("edit_theme/<int:userid>", views.edit_theme, name="edit-theme"),
    ### Autocomplete Views
    path(
        "user-autocomplete",
        views_autocomplete.UserAutocomplete.as_view(),
        name="user-autocomplete",
    ),
    path(
        "adherent-autocomplete",
        views_autocomplete.AdherentAutocomplete.as_view(),
        name="adherent-autocomplete",
    ),
    path(
        "club-autocomplete",
        views_autocomplete.ClubAutocomplete.as_view(),
        name="club-autocomplete",
    ),
    path(
        "school-autocomplete",
        views_autocomplete.SchoolAutocomplete.as_view(),
        name="school-autocomplete",
    ),
    path(
        "shell-autocomplete",
        views_autocomplete.ShellAutocomplete.as_view(),
        name="shell-autocomplete",
    ),
]
