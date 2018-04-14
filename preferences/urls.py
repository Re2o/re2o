# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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

import re2o
from . import views


urlpatterns = [
    url(
        r'^edit_options/(?P<section>OptionalUser)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>OptionalMachine)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>OptionalTopologie)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>GeneralOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>AssoOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>MailMessageOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(r'^add_service/$', views.add_service, name='add-service'),
    url(
        r'^edit_service/(?P<serviceid>[0-9]+)$',
        views.edit_service,
        name='edit-service'
        ),
    url(r'^del_services/$', views.del_services, name='del-services'),
    url(
        r'^history/(?P<object_name>\w+)/(?P<object_id>[0-9]+)$',
        re2o.views.history,
        name='history',
        kwargs={'application': 'preferences'},
        ),
    url(r'^$', views.display_options, name='display-options'),
]
