# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

from . import views

urls_viewset = [
    (r"topologie/stack", views.StackViewSet, None),
    (r"topologie/acesspoint", views.AccessPointViewSet, None),
    (r"topologie/switch", views.SwitchViewSet, None),
    (r"topologie/server", views.ServerViewSet, None),
    (r"topologie/modelswitch", views.ModelSwitchViewSet, None),
    (r"topologie/constructorswitch", views.ConstructorSwitchViewSet, None),
    (r"topologie/switchbay", views.SwitchBayViewSet, None),
    (r"topologie/building", views.BuildingViewSet, None),
    (r"topologie/switchport", views.SwitchPortViewSet, "switchport"),
    (r"topologie/portprofile", views.PortProfileViewSet, "portprofile"),
    (r"topologie/room", views.RoomViewSet, None)
]

urls_view = [
    # (r"topologie/portprofile", views.PortProfileViewSet)
    (r"topologie/switchs-ports-config", views.SwitchPortView),
    (r"topologie/switchs-role", views.RoleView),

    # Deprecated
    (r"switchs/ports-config", views.SwitchPortView),
    (r"switchs/role", views.RoleView),
]