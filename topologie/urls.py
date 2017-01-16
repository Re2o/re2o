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

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_switch/$', views.new_switch, name='new-switch'),
    url(r'^index_room/$', views.index_room, name='index-room'),
    url(r'^new_room/$', views.new_room, name='new-room'),
    url(r'^edit_room/(?P<room_id>[0-9]+)$', views.edit_room, name='edit-room'),
    url(r'^del_room/(?P<room_id>[0-9]+)$', views.del_room, name='del-room'),
    url(r'^switch/(?P<switch_id>[0-9]+)$', views.index_port, name='index-port'),
    url(r'^history/(?P<object>switch)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>port)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>room)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^edit_port/(?P<port_id>[0-9]+)$', views.edit_port, name='edit-port'),
    url(r'^new_port/(?P<switch_id>[0-9]+)$', views.new_port, name='new-port'),
    url(r'^edit_switch/(?P<switch_id>[0-9]+)$', views.edit_switch, name='edit-switch'),
]

