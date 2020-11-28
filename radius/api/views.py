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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from . import serializers
from machines.models import Domain, IpList, Interface, Nas
from users.models import User
from preferences.models import RadiusOption
from topologie.models import Port, Switch


class AuthorizeResponse:
    def __init__(self, nas, user, user_interface):
        self.nas = nas
        self.user = user
        self.user_interface = user_interface

    def can_view(self, user):
        return [True]


@api_view(['GET'])
def authorize(request, nas_id, username, mac_address):

    nas_interface = Interface.objects.filter(
        Q(domain=Domain.objects.filter(name=nas_id))
        | Q(ipv4=IpList.objects.filter(ipv4=nas_id))
    ).first()
    nas_type = None
    if nas_interface:
        nas_type = Nas.objects.filter(
            nas_type=nas_interface.machine_type).first()

    user = User.objects.filter(pseudo__iexact=username).first()
    user_interface = Interface.objects.filter(mac_address=mac_address).first()

    serialized = serializers.AuthorizeResponseSerializer(
        AuthorizeResponse(nas_type, user, user_interface))

    return Response(data=serialized.data)


class PostAuthResponse:
    def __init__(self, nas, room_users, port, port_profile, switch, user_interface, radius_option, EMAIL_STATE_UNVERIFIED, RADIUS_OPTION_REJECT, USER_STATE_ACTIVE):
        self.nas = nas
        self.room_users = room_users
        self.port = port
        self.port_profile = port_profile
        self.switch = switch
        self.user_interface = user_interface
        self.radius_option = radius_option
        self.EMAIL_STATE_UNVERIFIED = EMAIL_STATE_UNVERIFIED
        self.RADIUS_OPTION_REJECT = RADIUS_OPTION_REJECT
        self.USER_STATE_ACTIVE = USER_STATE_ACTIVE

    def can_view(self, user):
        return [True]


@api_view(['GET'])
def post_auth(request, nas_id, nas_port, user_mac):
    # get nas_type
    nas_interface = Interface.objects.prefetch_related("machine__switch__stack").filter(
        Q(domain=Domain.objects.filter(name=nas_id))
        | Q(ipv4=IpList.objects.filter(ipv4=nas_id))
    ).first()
    nas_type = None
    if nas_interface:
        nas_type = Nas.objects.filter(
            nas_type=nas_interface.machine_type).first()

    # get switch
    switch = None
    if nas_interface:
        switch = Switch.objects.filter(
            machine_ptr=nas_interface.machine).first()
        if hasattr(nas_interface.machine, "switch"):
            stack = nas_interface.machine.switch.stack
            if stack:
                id_stack_member = nas_port.split("-")[1].split("/")[0]
                switch = (
                    Switch.objects.filter(stack=stack)
                    .filter(stack_member_id=id_stack_member)
                    .first()
                )

    # get port
    port_number = nas_port.split(".")[0].split("/")[-1][-2:]
    port = Port.objects.filter(switch=switch, port=port_number).first()

    port_profile = None
    if port:
        port_profile = port.get_port_profile

    # get user_interface
    user_interface = (
        Interface.objects.filter(mac_address=user_mac)
        .select_related("machine__user")
        .select_related("ipv4")
        .first()
    )

    # get room users
    room_users = []
    if port:
        room_users = User.objects.filter(
            Q(club__room=port.room) | Q(adherent__room=port.room)
        )

    # get radius options
    radius_option = RadiusOption.objects.first()
    print(radius_option)

    EMAIL_STATE_UNVERIFIED = User.EMAIL_STATE_UNVERIFIED
    RADIUS_OPTION_REJECT = RadiusOption.REJECT
    USER_STATE_ACTIVE = User.STATE_ACTIVE
    serialized = serializers.PostAuthResponseSerializer(
        PostAuthResponse(nas_type, room_users, port, port_profile, switch, user_interface, radius_option, EMAIL_STATE_UNVERIFIED, RADIUS_OPTION_REJECT, USER_STATE_ACTIVE))

    return Response(data=serialized.data)
