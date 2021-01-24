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

from django.conf.urls import url

from . import views
from .views import edit_options


urlpatterns = [
    url(
        r"^edit_options/(?P<section>OptionalUser)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>OptionalMachine)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>OptionalTopologie)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>GeneralOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>AssoOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>HomeOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>MailMessageOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>RadiusOption)$",
        edit_options,
        name="edit-options",
    ),
    url(
        r"^edit_options/(?P<section>CotisationsOption)$",
        edit_options,
        name="edit-options",
    ),
    url(r"^add_service/$", views.add_service, name="add-service"),
    url(
        r"^edit_service/(?P<serviceid>[0-9]+)$", views.edit_service, name="edit-service"
    ),
    url(r"^del_service/(?P<serviceid>[0-9]+)$", views.del_service, name="del-service"),
    url(r"^add_mailcontact/$", views.add_mailcontact, name="add-mailcontact"),
    url(
        r"^edit_mailcontact/(?P<mailcontactid>[0-9]+)$",
        views.edit_mailcontact,
        name="edit-mailcontact",
    ),
    url(r"^del_mailcontact/$", views.del_mailcontact, name="del-mailcontact"),
    url(r"^add_reminder/$", views.add_reminder, name="add-reminder"),
    url(
        r"^edit_reminder/(?P<reminderid>[0-9]+)$",
        views.edit_reminder,
        name="edit-reminder",
    ),
    url(
        r"^del_reminder/(?P<reminderid>[0-9]+)$",
        views.del_reminder,
        name="del-reminder",
    ),
    url(r"^add_radiuskey/$", views.add_radiuskey, name="add-radiuskey"),
    url(
        r"^edit_radiuskey/(?P<radiuskeyid>[0-9]+)$",
        views.edit_radiuskey,
        name="edit-radiuskey",
    ),
    url(
        r"^del_radiuskey/(?P<radiuskeyid>[0-9]+)$",
        views.del_radiuskey,
        name="del-radiuskey",
    ),
    url(
        r"^add_switchmanagementcred/$",
        views.add_switchmanagementcred,
        name="add-switchmanagementcred",
    ),
    url(
        r"^edit_switchmanagementcred/(?P<switchmanagementcredid>[0-9]+)$",
        views.edit_switchmanagementcred,
        name="edit-switchmanagementcred",
    ),
    url(
        r"^del_switchmanagementcred/(?P<switchmanagementcredid>[0-9]+)$",
        views.del_switchmanagementcred,
        name="del-switchmanagementcred",
    ),
    url(
        r"^add_document_template/$",
        views.add_document_template,
        name="add-document-template",
    ),
    url(
        r"^edit_document_template/(?P<documenttemplateid>[0-9]+)$",
        views.edit_document_template,
        name="edit-document-template",
    ),
    url(
        r"^del_document_template/$",
        views.del_document_template,
        name="del-document-template",
    ),
    url(r"^add_mandate/$", views.add_mandate, name="add-mandate"),
    url(
        r"^edit_mandate/(?P<mandateid>[0-9]+)$", views.edit_mandate, name="edit-mandate"
    ),
    url(r"^del_mandate/(?P<mandateid>[0-9]+)$", views.del_mandate, name="del-mandate"),
    url(
        r"^add_radiusattribute/$", views.add_radiusattribute, name="add-radiusattribute"
    ),
    url(
        r"^edit_radiusattribute/(?P<radiusattributeid>[0-9]+)$",
        views.edit_radiusattribute,
        name="edit-radiusattribute",
    ),
    url(
        r"^del_radiusattribute/(?P<radiusattributeid>[0-9]+)$",
        views.del_radiusattribute,
        name="del-radiusattribute",
    ),
    url(r"^$", views.display_options, name="display-options"),
]
