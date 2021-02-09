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
"""
Urls de l'application preferences, pointant vers les fonctions de views
"""

from __future__ import unicode_literals

from django.urls import path, re_path

from . import views
from .views import edit_options

app_name = "preferences"

urlpatterns = [
    re_path(
        r"^edit_options/(?P<section>OptionalUser)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>OptionalMachine)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>OptionalTopologie)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>GeneralOption)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>AssoOption)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>HomeOption)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>MailMessageOption)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>RadiusOption)$",
        edit_options,
        name="edit-options",
    ),
    re_path(
        r"^edit_options/(?P<section>CotisationsOption)$",
        edit_options,
        name="edit-options",
    ),
    path("add_service", views.add_service, name="add-service"),
    path(
        "edit_service/<int:serviceid>", views.edit_service, name="edit-service"
    ),
    path("del_service/<int:serviceid>", views.del_service, name="del-service"),
    path("add_mailcontact", views.add_mailcontact, name="add-mailcontact"),
    path(
        "edit_mailcontact/<int:mailcontactid>",
        views.edit_mailcontact,
        name="edit-mailcontact",
    ),
    path("del_mailcontact", views.del_mailcontact, name="del-mailcontact"),
    path("add_reminder", views.add_reminder, name="add-reminder"),
    path(
        "edit_reminder/<int:reminderid>",
        views.edit_reminder,
        name="edit-reminder",
    ),
    path(
        "del_reminder/<int:reminderid>",
        views.del_reminder,
        name="del-reminder",
    ),
    path("add_radiuskey", views.add_radiuskey, name="add-radiuskey"),
    path(
        "edit_radiuskey/<int:radiuskeyid>",
        views.edit_radiuskey,
        name="edit-radiuskey",
    ),
    path(
        "del_radiuskey/<int:radiuskeyid>",
        views.del_radiuskey,
        name="del-radiuskey",
    ),
    path(
        "add_switchmanagementcred",
        views.add_switchmanagementcred,
        name="add-switchmanagementcred",
    ),
    path(
        "edit_switchmanagementcred/<int:switchmanagementcredid>",
        views.edit_switchmanagementcred,
        name="edit-switchmanagementcred",
    ),
    path(
        "del_switchmanagementcred/<int:switchmanagementcredid>",
        views.del_switchmanagementcred,
        name="del-switchmanagementcred",
    ),
    path(
        "add_document_template",
        views.add_document_template,
        name="add-document-template",
    ),
    path(
        "edit_document_template/<int:documenttemplateid>",
        views.edit_document_template,
        name="edit-document-template",
    ),
    path(
        "del_document_template",
        views.del_document_template,
        name="del-document-template",
    ),
    path("add_mandate", views.add_mandate, name="add-mandate"),
    path(
        "edit_mandate/<int:mandateid>", views.edit_mandate, name="edit-mandate"
    ),
    path("del_mandate/<int:mandateid>", views.del_mandate, name="del-mandate"),
    path(
        "add_radiusattribute", views.add_radiusattribute, name="add-radiusattribute"
    ),
    path(
        "edit_radiusattribute/<int:radiusattributeid>",
        views.edit_radiusattribute,
        name="edit-radiusattribute",
    ),
    path(
        "del_radiusattribute/<int:radiusattributeid>",
        views.del_radiusattribute,
        name="del-radiusattribute",
    ),
    path("", views.display_options, name="display-options"),
]
