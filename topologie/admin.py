# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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
"""topologie.admin
The objects, fields and datastructures visible in the Django admin view.
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    Port,
    Room,
    Switch,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint,
    SwitchBay,
    Building,
    Dormitory,
    PortProfile,
)


class StackAdmin(VersionAdmin):
    """Admin class of stacks (includes switches)."""

    pass


class SwitchAdmin(VersionAdmin):
    """Admin class of switches."""

    pass


class PortAdmin(VersionAdmin):
    """Admin class of switch ports."""

    pass


class AccessPointAdmin(VersionAdmin):
    """Admin class of APs."""

    pass


class RoomAdmin(VersionAdmin):
    """Admin class of rooms."""

    pass


class ModelSwitchAdmin(VersionAdmin):
    """Admin class of switch models."""

    pass


class ConstructorSwitchAdmin(VersionAdmin):
    """Admin class of switch constructors."""

    pass


class SwitchBayAdmin(VersionAdmin):
    """Admin class of switch bays."""

    pass


class BuildingAdmin(VersionAdmin):
    """Admin class of buildings."""

    pass


class DormitoryAdmin(VersionAdmin):
    """Admin class of dormitories."""

    pass


class PortProfileAdmin(VersionAdmin):
    """Admin class of port profiles."""

    pass


admin.site.register(Port, PortAdmin)
admin.site.register(AccessPoint, AccessPointAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Stack, StackAdmin)
admin.site.register(ModelSwitch, ModelSwitchAdmin)
admin.site.register(ConstructorSwitch, ConstructorSwitchAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Dormitory, DormitoryAdmin)
admin.site.register(SwitchBay, SwitchBayAdmin)
admin.site.register(PortProfile, PortProfileAdmin)
