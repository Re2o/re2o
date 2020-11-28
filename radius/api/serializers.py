# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020 Corentin Canebier
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

import machines.models as machines
import users.models as users
from api.serializers import NamespacedHMSerializer
from rest_framework.serializers import Serializer


class Ipv4Serializer(Serializer):
    ipv4 = serializers.CharField()


class InterfaceSerializer(Serializer):
    mac_address = serializers.CharField()
    ipv4 = Ipv4Serializer()
    active = serializers.BooleanField(source="is_active")
    user_pk = serializers.CharField(source="machine.user.pk")
    machine_short_name = serializers.CharField(source="machine.short_name")
    is_ban = serializers.BooleanField(source="machine.user.is_ban")
    vlan_id = serializers.IntegerField(
        source="machine_type.ip_type.vlan.vlan_id")


class NasSerializer(Serializer):
    port_access_mode = serializers.CharField()
    autocapture_mac = serializers.BooleanField()


class UserSerializer(Serializer):
    access = serializers.BooleanField(source="has_access")
    pk = serializers.CharField()
    pwd_ntlm = serializers.CharField()
    state = serializers.CharField()
    email_state = serializers.IntegerField()
    is_ban = serializers.BooleanField()
    is_connected = serializers.BooleanField()
    is_whitelisted = serializers.BooleanField()


class PortSerializer(Serializer):
    state = serializers.BooleanField()
    room = serializers.CharField()


class VlanSerializer(Serializer):
    vlan_id = serializers.IntegerField()


class PortProfileSerializer(Serializer):
    vlan_untagged = VlanSerializer()
    radius_type = serializers.CharField()
    radius_mode = serializers.CharField()


class SwitchSerializer(Serializer):
    name = serializers.CharField(source="short_name")
    ipv4 = serializers.CharField()


class RadiusAttributeSerializer(Serializer):
    attribute = serializers.CharField()
    value = serializers.CharField()


class RadiusOptionSerializer(Serializer):
    radius_general_policy = serializers.CharField()
    unknown_machine = serializers.CharField()
    unknown_machine_vlan = VlanSerializer()
    unknown_machine_attributes = RadiusAttributeSerializer(many=True)
    unknown_port = serializers.CharField()
    unknown_port_vlan = VlanSerializer()
    unknown_port_attributes = RadiusAttributeSerializer(many=True)
    unknown_room = serializers.CharField()
    unknown_room_vlan = VlanSerializer()
    unknown_room_attributes = RadiusAttributeSerializer(many=True)
    non_member = serializers.CharField()
    non_member_vlan = VlanSerializer()
    non_member_attributes = RadiusAttributeSerializer(many=True)
    banned = serializers.CharField()
    banned_vlan = VlanSerializer()
    banned_attributes = RadiusAttributeSerializer(many=True)
    vlan_decision_ok = VlanSerializer()
    ok_attributes = RadiusAttributeSerializer(many=True)


class AuthorizeResponseSerializer(Serializer):
    nas = NasSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    user_interface = InterfaceSerializer(read_only=True)


class PostAuthResponseSerializer(Serializer):
    nas = NasSerializer(read_only=True)
    room_users = UserSerializer(many=True)
    port = PortSerializer()
    port_profile = PortProfileSerializer(partial=True)
    switch = SwitchSerializer()
    user_interface = InterfaceSerializer()
    radius_option = RadiusOptionSerializer()
    EMAIL_STATE_UNVERIFIED = serializers.IntegerField()
    RADIUS_OPTION_REJECT = serializers.CharField()
    USER_STATE_ACTIVE = serializers.CharField()
