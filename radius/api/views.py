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
from django.http import HttpResponse
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required

from . import serializers
from machines.models import Domain, IpList, Interface, Nas, Machine
from users.models import User
from preferences.models import RadiusOption
from topologie.models import Port, Switch
from re2o.acl import can_view_all_api, can_edit_all_api, can_create_api


class AuthorizeResponse:
    """Contains objects the radius needs for the Authorize step"""

    def __init__(self, nas, user, user_interface):
        self.nas = nas
        self.user = user
        self.user_interface = user_interface

    def can_view(self, user):
        """Method to bypass api permissions, because we are using ACL decorators"""
        return (True, None, None)


@api_view(["GET"])
@login_required
@can_view_all_api(Interface, Domain, IpList, Nas, User)
def authorize(request, nas_id, username, mac_address):
    """Return objects the radius needs for the Authorize step

    Parameters:
        nas_id (string): NAS name or ipv4
        username (string): username of the user who is trying to connect
        mac_address (string): mac address of the device which is trying to connect

    Return:
        AuthorizeResponse: contains all required informations
    """

    # get the Nas object which made the request (if exists)
    nas_interface = Interface.objects.filter(
        Q(domain__name=nas_id) | Q(ipv4__ipv4=nas_id)
    ).first()
    nas_type = None
    if nas_interface:
        nas_type = Nas.objects.filter(nas_type=nas_interface.machine_type).first()

    # get the User corresponding to the username in the URL
    # If no username was provided (wired connection), username="None"
    user = User.objects.filter(pseudo__iexact=username).first()

    # get the interface which is trying to connect (if already created)
    user_interface = Interface.objects.filter(mac_address=mac_address).first()

    serialized = serializers.AuthorizeResponseSerializer(
        AuthorizeResponse(nas_type, user, user_interface)
    )

    return Response(data=serialized.data)


class PostAuthResponse:
    """Contains objects the radius needs for the Post-Auth step"""

    def __init__(
        self,
        nas,
        room_users,
        port,
        port_profile,
        switch,
        user_interface,
        radius_option,
        EMAIL_STATE_UNVERIFIED,
        RADIUS_OPTION_REJECT,
        USER_STATE_ACTIVE,
    ):
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
        """Method to bypass api permissions, because we are using ACL decorators"""
        return (True, None, None)


@api_view(["GET"])
@login_required
@can_view_all_api(Interface, Domain, IpList, Nas, Switch, Port, User)
def post_auth(request, nas_id, nas_port, user_mac):
    """Return objects the radius needs for the Post-Auth step

    Parameters:
        nas_id (string): NAS name or ipv4
        nas_port (string): NAS port from wich the request came. Work with Cisco, HP and Juniper convention
        user_mac (string): mac address of the device which is trying to connect

    Return:
        PostAuthResponse: contains all required informations
    """

    # get the Nas object which made the request (if exists)
    nas_interface = (
        Interface.objects.prefetch_related("machine__switch__stack")
        .filter(Q(domain__name=nas_id) | Q(ipv4__ipv4=nas_id))
        .first()
    )
    nas_type = None
    if nas_interface:
        nas_type = Nas.objects.filter(nas_type=nas_interface.machine_type).first()

    # get the switch (if wired connection)
    switch = None
    if nas_interface:
        switch = Switch.objects.filter(machine_ptr=nas_interface.machine).first()

        # If the switch is part of a stack, get the correct object
        if hasattr(nas_interface.machine, "switch"):
            stack = nas_interface.machine.switch.stack
            if stack:
                # For Juniper, the result looks something like this: NAS-Port-Id = "ge-0/0/6.0""
                # For other brands (e.g. HP or Mikrotik), the result usually looks like: NAS-Port-Id = "6.0"
                # This "magic split" handles both cases
                # Cisco can rot in Hell for all I care, so their format is not supported (it looks like NAS-Port-ID = atm 31/31/7:255.65535 guangzhou001/0/31/63/31/127)
                id_stack_member = nas_port.split("-")[1].split("/")[0]
                switch = (
                    Switch.objects.filter(stack=stack)
                    .filter(stack_member_id=id_stack_member)
                    .first()
                )

    # get the switch port
    port = None
    if nas_port and nas_port != "None":
        # magic split (see above)
        port_number = nas_port.split(".")[0].split("/")[-1][-2:]
        port = Port.objects.filter(switch=switch, port=port_number).first()

    port_profile = None
    if port:
        port_profile = port.get_port_profile

    # get the interface which is trying to connect (if already created)
    user_interface = (
        Interface.objects.filter(mac_address=user_mac)
        .select_related("machine__user")
        .select_related("ipv4")
        .first()
    )

    # get all users and clubs of the room
    room_users = []
    if port:
        room_users = User.objects.filter(
            Q(club__room=port.room) | Q(adherent__room=port.room)
        )

    # get all radius options
    radius_option = RadiusOption.objects.first()

    # get a few class constants the radius will need
    EMAIL_STATE_UNVERIFIED = User.EMAIL_STATE_UNVERIFIED
    RADIUS_OPTION_REJECT = RadiusOption.REJECT
    USER_STATE_ACTIVE = User.STATE_ACTIVE

    serialized = serializers.PostAuthResponseSerializer(
        PostAuthResponse(
            nas_type,
            room_users,
            port,
            port_profile,
            switch,
            user_interface,
            radius_option,
            EMAIL_STATE_UNVERIFIED,
            RADIUS_OPTION_REJECT,
            USER_STATE_ACTIVE,
        )
    )

    return Response(data=serialized.data)


@api_view(["GET"])
@login_required
@can_view_all_api(Interface, Domain, IpList, Nas, User)
@can_edit_all_api(User, Domain, Machine, Interface)
def autoregister_machine(request, nas_id, username, mac_address):
    """Autoregister machine in the Authorize step of the radius

    Parameters:
        nas_id (string): NAS name or ipv4
        username (string): username of the user who is trying to connect
        mac_address (string): mac address of the device which is trying to connect

    Return:
        200 if autoregistering worked
        400 if it failed, and the reason why
    """
    nas_interface = Interface.objects.filter(
        Q(domain__name=nas_id) | Q(ipv4__ipv4=nas_id)
    ).first()
    nas_type = None
    if nas_interface:
        nas_type = Nas.objects.filter(nas_type=nas_interface.machine_type).first()

    user = User.objects.filter(pseudo__iexact=username).first()

    result, reason = user.autoregister_machine(mac_address, nas_type)
    if result:
        return Response(reason)
    return Response(reason, status=400)


@api_view(["GET"])
@can_view_all_api(Interface)
@can_edit_all_api(Interface)
def assign_ip(request, mac_address):
    """Autoassign ip in the Authorize and Post-Auth steps of the Radius

    Parameters:
        mac_address (string): mac address of the device which is trying to connect

    Return:
        200 if it worked
        400 if it failed, and the reason why
    """
    interface = Interface.objects.filter(mac_address=mac_address).first()

    try:
        interface.assign_ipv4()
        return Response()
    except ValidationError as err:
        return Response(err.message, status=400)
