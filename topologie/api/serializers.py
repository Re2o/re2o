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

from rest_framework import serializers

import topologie.models as topologie
import machines.models as machines
from machines.api.serializers import VlanSerializer, Ipv6ListSerializer
from api.serializers import NamespacedHRField, NamespacedHIField, NamespacedHMSerializer


class StackSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Stack` objects
    """

    class Meta:
        model = topologie.Stack
        fields = (
            "name",
            "stack_id",
            "details",
            "member_id_min",
            "member_id_max",
            "api_url",
        )


class AccessPointSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.AccessPoint` objects
    """

    class Meta:
        model = topologie.AccessPoint
        fields = ("user", "name", "active", "location", "api_url")


class SwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Switch` objects
    """

    port_amount = serializers.IntegerField(source="number")

    class Meta:
        model = topologie.Switch
        fields = (
            "user",
            "name",
            "active",
            "port_amount",
            "stack",
            "stack_member_id",
            "model",
            "switchbay",
            "api_url",
        )


class ServerSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Server` objects
    """

    class Meta:
        model = topologie.Server
        fields = ("user", "name", "active", "api_url")


class ModelSwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.ModelSwitch` objects
    """

    class Meta:
        model = topologie.ModelSwitch
        fields = ("reference", "constructor", "api_url")


class ConstructorSwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.ConstructorSwitch` objects
    """

    class Meta:
        model = topologie.ConstructorSwitch
        fields = ("name", "api_url")


class SwitchBaySerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.SwitchBay` objects
    """

    class Meta:
        model = topologie.SwitchBay
        fields = ("name", "building", "info", "api_url")


class BuildingSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Building` objects
    """

    class Meta:
        model = topologie.Building
        fields = ("name", "dormitory", "api_url")

class DormitorySerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Dormitory` objects
    """
    class Meta:
        model = topologie.Dormitory
        fields = ("name", "api_url")

class PortProfileSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Room` objects
    """

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "api_url",
        )


class RoomSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Room` objects
    """

    class Meta:
        model = topologie.Room
        fields = ("name", "building", "details", "api_url")


class PortProfileSerializer(NamespacedHMSerializer):
    vlan_untagged = VlanSerializer(read_only=True)

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "vlan_untagged",
            "vlan_tagged",
        )


class InterfaceVlanSerializer(NamespacedHMSerializer):
    domain = serializers.CharField(read_only=True)
    ipv4 = serializers.CharField(read_only=True)
    ipv6 = Ipv6ListSerializer(read_only=True, many=True)
    vlan_id = serializers.IntegerField(
        source="machine_type.ip_type.vlan.vlan_id", read_only=True
    )

    class Meta:
        model = machines.Interface
        fields = ("ipv4", "ipv6", "domain", "vlan_id")


class InterfaceRoleSerializer(NamespacedHMSerializer):
    interface = InterfaceVlanSerializer(
        source="machine.interface_set", read_only=True, many=True
    )

    class Meta:
        model = machines.Interface
        fields = ("interface",)


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    servers = InterfaceRoleSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ("role_type", "servers", "specific_role")


class VlanPortSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Vlan
        fields = ("vlan_id", "name")


class ProfilSerializer(NamespacedHMSerializer):
    vlan_untagged = VlanSerializer(read_only=True)
    vlan_tagged = VlanPortSerializer(read_only=True, many=True)

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "vlan_untagged",
            "vlan_tagged",
        )


class ModelSwitchSerializer(NamespacedHMSerializer):
    constructor = serializers.CharField(read_only=True)

    class Meta:
        model = topologie.ModelSwitch
        fields = ("reference", "firmware", "constructor")


class SwitchBaySerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.SwitchBay
        fields = ("name",)


class PortsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """

    get_port_profile = ProfilSerializer(read_only=True)

    class Meta:
        model = topologie.Port
        fields = ("state", "port", "pretty_name", "get_port_profile")


class SwitchPortSerializer(serializers.ModelSerializer):
    """Serialize the data about the switches"""

    ports = PortsSerializer(many=True, read_only=True)
    model = ModelSwitchSerializer(read_only=True)
    switchbay = SwitchBaySerializer(read_only=True)

    class Meta:
        model = topologie.Switch
        fields = (
            "short_name",
            "model",
            "switchbay",
            "ports",
            "ipv4",
            "ipv6",
            "interfaces_subnet",
            "interfaces6_subnet",
            "automatic_provision",
            "rest_enabled",
            "web_management_enabled",
            "get_radius_key_value",
            "get_management_cred_value",
            "get_radius_servers",
            "list_modules",
        )


