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
Definition des urls de l'application topologie.
Inclu dans urls de re2o.

Fait référence aux fonctions du views
"""

from __future__ import unicode_literals

from django.conf.urls import url

import re2o
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index_ap/$', views.index_ap, name='index-ap'),
    url(r'^new_ap/$', views.new_ap, name='new-ap'),
    url(r'^edit_ap/(?P<accesspoint_id>[0-9]+)$',
        views.edit_ap,
        name='edit-ap'),
    url(r'^create_ports/(?P<switch_id>[0-9]+)$',
        views.create_ports,
        name='create-ports'),
    url(r'^index_room/$', views.index_room, name='index-room'),
    url(r'^new_room/$', views.new_room, name='new-room'),
    url(r'^edit_room/(?P<room_id>[0-9]+)$', views.edit_room, name='edit-room'),
    url(r'^del_room/(?P<room_id>[0-9]+)$', views.del_room, name='del-room'),
    url(r'^new_switch/$', views.new_switch, name='new-switch'),
    url(r'^switch/(?P<switch_id>[0-9]+)$',
        views.index_port,
        name='index-port'),
    url(
        r'^history/(?P<object_name>\w+)/(?P<object_id>[0-9]+)$',
        re2o.views.history,
        name='history',
        kwargs={'application':'topologie'},
    ),
    url(r'^edit_port/(?P<port_id>[0-9]+)$', views.edit_port, name='edit-port'),
    url(r'^new_port/(?P<switch_id>[0-9]+)$', views.new_port, name='new-port'),
    url(r'^del_port/(?P<port_id>[0-9]+)$', views.del_port, name='del-port'),
    url(r'^edit_switch/(?P<switch_id>[0-9]+)$',
        views.edit_switch,
        name='edit-switch'),
    url(r'^new_stack/$', views.new_stack, name='new-stack'),
    url(r'^index_stack/$', views.index_stack, name='index-stack'),
    url(r'^edit_stack/(?P<stack_id>[0-9]+)$',
        views.edit_stack,
        name='edit-stack'),
    url(r'^del_stack/(?P<stack_id>[0-9]+)$',
        views.del_stack,
        name='del-stack'),
    url(r'^index_model_switch/$',
        views.index_model_switch,
        name='index-model-switch'
    ),
    url(r'^index_model_switch/$',
        views.index_model_switch,
        name='index-model-switch'
    ),
    url(r'^new_model_switch/$',
        views.new_model_switch,
        name='new-model-switch'
    ),
    url(r'^edit_model_switch/(?P<model_switch_id>[0-9]+)$',
        views.edit_model_switch,
        name='edit-model-switch'),
    url(r'^del_model_switch/(?P<model_switch_id>[0-9]+)$',
        views.del_model_switch,
        name='del-model-switch'),
    url(r'^new_constructor_switch/$',
        views.new_constructor_switch,
        name='new-constructor-switch'
    ),
    url(r'^edit_constructor_switch/(?P<constructor_switch_id>[0-9]+)$',
        views.edit_constructor_switch,
        name='edit-constructor-switch'),
    url(r'^del_constructor_switch/(?P<constructor_switch_id>[0-9]+)$',
        views.del_constructor_switch,
        name='del-constructor-switch'),
]
