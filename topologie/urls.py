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

from django.urls import path

from . import views
from . import views_autocomplete

app_name = "topologie"

urlpatterns = [
    path("", views.index, name="index"),
    path("index_ap", views.index_ap, name="index-ap"),
    path("new_ap", views.new_ap, name="new-ap"),
    path("edit_ap/<int:accesspointid>", views.edit_ap, name="edit-ap"),
    path(
        "create_ports/<int:switchid>", views.create_ports, name="create-ports"
    ),
    path("index_room", views.index_room, name="index-room"),
    path("new_room", views.new_room, name="new-room"),
    path("edit_room/<int:roomid>", views.edit_room, name="edit-room"),
    path("del_room/<int:roomid>", views.del_room, name="del-room"),
    path("new_switch", views.new_switch, name="new-switch"),
    path("switch/<int:switchid>", views.index_port, name="index-port"),
    path("edit_port/<int:portid>", views.edit_port, name="edit-port"),
    path("new_port/<int:switchid>", views.new_port, name="new-port"),
    path("del_port/<int:portid>", views.del_port, name="del-port"),
    path("edit_switch/<int:switchid>", views.edit_switch, name="edit-switch"),
    path("new_stack", views.new_stack, name="new-stack"),
    path(
        "index_stack",
        views.index_stack,
        name="index-stack",
    ),
    path(
        "index_switch_bay",
        views.index_switch_bay,
        name="index-switch-bay",
    ),
    path(
        "index_building",
        views.index_building,
        name="index-building",
    ),
    path(
        "index_dormitory",
        views.index_dormitory,
        name="index-dormitory",
    ),
    path("edit_stack/<int:stackid>", views.edit_stack, name="edit-stack"),
    path("del_stack/<int:stackid>", views.del_stack, name="del-stack"),
    path("index_model_switch", views.index_model_switch, name="index-model-switch"),
    path("index_model_switch", views.index_model_switch, name="index-model-switch"),
    path("new_model_switch", views.new_model_switch, name="new-model-switch"),
    path(
        "edit_model_switch/<int:modelswitchid>",
        views.edit_model_switch,
        name="edit-model-switch",
    ),
    path(
        "del_model_switch/<int:modelswitchid>",
        views.del_model_switch,
        name="del-model-switch",
    ),
    path(
        "new_constructor_switch",
        views.new_constructor_switch,
        name="new-constructor-switch",
    ),
    path(
        "edit_constructor_switch/<int:constructorswitchid>",
        views.edit_constructor_switch,
        name="edit-constructor-switch",
    ),
    path(
        "del_constructor_switch/<int:constructorswitchid>",
        views.del_constructor_switch,
        name="del-constructor-switch",
    ),
    path("new_switch_bay", views.new_switch_bay, name="new-switch-bay"),
    path(
        "edit_switch_bay/<int:switchbayid>",
        views.edit_switch_bay,
        name="edit-switch-bay",
    ),
    path(
        "del_switch_bay/<int:switchbayid>",
        views.del_switch_bay,
        name="del-switch-bay",
    ),
    path("new_building", views.new_building, name="new-building"),
    path(
        "edit_building/<int:buildingid>",
        views.edit_building,
        name="edit-building",
    ),
    path(
        "del_building/<int:buildingid>",
        views.del_building,
        name="del-building",
    ),
    path("new_dormitory", views.new_dormitory, name="new-dormitory"),
    path(
        "edit_dormitory/<int:dormitoryid>",
        views.edit_dormitory,
        name="edit-dormitory",
    ),
    path(
        "del_dormitory/<int:dormitoryid>",
        views.del_dormitory,
        name="del-dormitory",
    ),
    path("index_port_profile", views.index_port_profile, name="index-port-profile"),
    path("new_port_profile", views.new_port_profile, name="new-port-profile"),
    path(
        "edit_port_profile/<int:portprofileid>",
        views.edit_port_profile,
        name="edit-port-profile",
    ),
    path(
        "del_port_profile/<int:portprofileid>",
        views.del_port_profile,
        name="del-port-profile",
    ),
    path(
        "edit_vlanoptions/<int:vlanid>",
        views.edit_vlanoptions,
        name="edit-vlanoptions",
    ),
    path("add_module", views.add_module, name="add-module"),
    path(
        "edit_module/<int:moduleswitchid>",
        views.edit_module,
        name="edit-module",
    ),
    path(
        "del_module/<int:moduleswitchid>", views.del_module, name="del-module"
    ),
    path("index_module", views.index_module, name="index-module"),
    path("add_module_on", views.add_module_on, name="add-module-on"),
    path(
        "edit_module_on/<int:moduleonswitchid>",
        views.edit_module_on,
        name="edit-module-on",
    ),
    path(
        "del_module_on/<int:moduleonswitchid>",
        views.del_module_on,
        name="del-module-on",
    ),
    ### Autocomplete Views
    path('room-autocomplete', views_autocomplete.RoomAutocomplete.as_view(), name='room-autocomplete',),
    path('building-autocomplete', views_autocomplete.BuildingAutocomplete.as_view(), name='building-autocomplete',),
    path('dormitory-autocomplete', views_autocomplete.DormitoryAutocomplete.as_view(), name='dormitory-autocomplete',),
    path('switch-autocomplete', views_autocomplete.SwitchAutocomplete.as_view(), name='switch-autocomplete',),
    path('port-autocomplete', views_autocomplete.PortAutocomplete.as_view(), name='profile-autocomplete',),
    path('portprofile-autocomplete', views_autocomplete.PortProfileAutocomplete.as_view(), name='portprofile-autocomplete',),
    path('switchbay-autocomplete', views_autocomplete.SwitchBayAutocomplete.as_view(), name='switchbay-autocomplete',),
]
