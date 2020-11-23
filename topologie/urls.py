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
"""topologie.urls
The defined URLs for topologie app. Included in re2o.urls.
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^index_ap/$", views.index_ap, name="index-ap"),
    url(r"^new_ap/$", views.new_ap, name="new-ap"),
    url(r"^edit_ap/(?P<accesspointid>[0-9]+)$", views.edit_ap, name="edit-ap"),
    url(
        r"^create_ports/(?P<switchid>[0-9]+)$", views.create_ports, name="create-ports"
    ),
    url(r"^index_room/$", views.index_room, name="index-room"),
    url(r"^new_room/$", views.new_room, name="new-room"),
    url(r"^edit_room/(?P<roomid>[0-9]+)$", views.edit_room, name="edit-room"),
    url(r"^del_room/(?P<roomid>[0-9]+)$", views.del_room, name="del-room"),
    url(r"^new_switch/$", views.new_switch, name="new-switch"),
    url(r"^switch/(?P<switchid>[0-9]+)$", views.index_port, name="index-port"),
    url(r"^edit_port/(?P<portid>[0-9]+)$", views.edit_port, name="edit-port"),
    url(r"^new_port/(?P<switchid>[0-9]+)$", views.new_port, name="new-port"),
    url(r"^del_port/(?P<portid>[0-9]+)$", views.del_port, name="del-port"),
    url(r"^edit_switch/(?P<switchid>[0-9]+)$", views.edit_switch, name="edit-switch"),
    url(r"^new_stack/$", views.new_stack, name="new-stack"),
    url(
        r"^index_stack/$",
        views.index_stack,
        name="index-stack",
    ),
    url(
        r"^index_switch_bay/$",
        views.index_switch_bay,
        name="index-switch-bay",
    ),
    url(
        r"^index_building/$",
        views.index_building,
        name="index-building",
    ),
    url(
        r"^index_dormitory/$",
        views.index_dormitory,
        name="index-dormitory",
    ),
    url(r"^edit_stack/(?P<stackid>[0-9]+)$", views.edit_stack, name="edit-stack"),
    url(r"^del_stack/(?P<stackid>[0-9]+)$", views.del_stack, name="del-stack"),
    url(r"^index_model_switch/$", views.index_model_switch, name="index-model-switch"),
    url(r"^index_model_switch/$", views.index_model_switch, name="index-model-switch"),
    url(r"^new_model_switch/$", views.new_model_switch, name="new-model-switch"),
    url(
        r"^edit_model_switch/(?P<modelswitchid>[0-9]+)$",
        views.edit_model_switch,
        name="edit-model-switch",
    ),
    url(
        r"^del_model_switch/(?P<modelswitchid>[0-9]+)$",
        views.del_model_switch,
        name="del-model-switch",
    ),
    url(
        r"^new_constructor_switch/$",
        views.new_constructor_switch,
        name="new-constructor-switch",
    ),
    url(
        r"^edit_constructor_switch/(?P<constructorswitchid>[0-9]+)$",
        views.edit_constructor_switch,
        name="edit-constructor-switch",
    ),
    url(
        r"^del_constructor_switch/(?P<constructorswitchid>[0-9]+)$",
        views.del_constructor_switch,
        name="del-constructor-switch",
    ),
    url(r"^new_switch_bay/$", views.new_switch_bay, name="new-switch-bay"),
    url(
        r"^edit_switch_bay/(?P<switchbayid>[0-9]+)$",
        views.edit_switch_bay,
        name="edit-switch-bay",
    ),
    url(
        r"^del_switch_bay/(?P<switchbayid>[0-9]+)$",
        views.del_switch_bay,
        name="del-switch-bay",
    ),
    url(r"^new_building/$", views.new_building, name="new-building"),
    url(
        r"^edit_building/(?P<buildingid>[0-9]+)$",
        views.edit_building,
        name="edit-building",
    ),
    url(
        r"^del_building/(?P<buildingid>[0-9]+)$",
        views.del_building,
        name="del-building",
    ),
    url(r"^new_dormitory/$", views.new_dormitory, name="new-dormitory"),
    url(
        r"^edit_dormitory/(?P<dormitoryid>[0-9]+)$",
        views.edit_dormitory,
        name="edit-dormitory",
    ),
    url(
        r"^del_dormitory/(?P<dormitoryid>[0-9]+)$",
        views.del_dormitory,
        name="del-dormitory",
    ),
    url(r"^index_port_profile/$", views.index_port_profile, name="index-port-profile"),
    url(r"^new_port_profile/$", views.new_port_profile, name="new-port-profile"),
    url(
        r"^edit_port_profile/(?P<portprofileid>[0-9]+)$",
        views.edit_port_profile,
        name="edit-port-profile",
    ),
    url(
        r"^del_port_profile/(?P<portprofileid>[0-9]+)$",
        views.del_port_profile,
        name="del-port-profile",
    ),
    url(
        r"^edit_vlanoptions/(?P<vlanid>[0-9]+)$",
        views.edit_vlanoptions,
        name="edit-vlanoptions",
    ),
    url(r"^add_module/$", views.add_module, name="add-module"),
    url(
        r"^edit_module/(?P<moduleswitchid>[0-9]+)$",
        views.edit_module,
        name="edit-module",
    ),
    url(
        r"^del_module/(?P<moduleswitchid>[0-9]+)$", views.del_module, name="del-module"
    ),
    url(r"^index_module/$", views.index_module, name="index-module"),
    url(r"^add_module_on/$", views.add_module_on, name="add-module-on"),
    url(
        r"^edit_module_on/(?P<moduleonswitchid>[0-9]+)$",
        views.edit_module_on,
        name="edit-module-on",
    ),
    url(
        r"^del_module_on/(?P<moduleonswitchid>[0-9]+)$",
        views.del_module_on,
        name="del-module-on",
    ),
]
