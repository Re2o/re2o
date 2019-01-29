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

"""Defines the views of the API

All views inherits the `rest_framework.views.APIview` to respect the
REST API requirements such as dealing with HTTP status code, format of
the response (JSON or other), the CSRF exempting, ...
"""

import datetime

from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users
from re2o.utils import all_active_interfaces, all_has_access
from . import serializers
from .pagination import PageSizedPagination
from .permissions import ACLPermission

# SERVICE REGEN

class ServiceRegenViewSet(viewsets.ModelViewSet):
    """Exposes list and details of the services to regen
    """
    serializer_class = serializers.ServiceRegenSerializer

    def get_queryset(self):
        queryset = machines.Service_link.objects.select_related(
            'server__domain'
        ).select_related(
            'service'
        )
        if 'hostname' in self.request.GET:
            hostname = self.request.GET['hostname']
            queryset = queryset.filter(server__domain__name__iexact=hostname)
        return queryset

# Config des switches

class SwitchPortView(generics.ListAPIView):
    """Output each port of a switch, to be serialized with
    additionnal informations (profiles etc)
    """
    queryset = topologie.Switch.objects.all().select_related("switchbay").select_related("model__constructor").prefetch_related("ports__custom_profile__vlan_tagged").prefetch_related("ports__custom_profile__vlan_untagged").prefetch_related("ports__machine_interface__domain__extension").prefetch_related("ports__room")

    serializer_class = serializers.SwitchPortSerializer

# Rappel fin adhésion

class ReminderView(generics.ListAPIView):
    """Output for users to remind an end of their subscription.
    """
    queryset = preferences.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer


class RoleView(generics.ListAPIView):
    """Output of roles for each server
    """
    queryset = machines.Role.objects.all().prefetch_related('servers')
    serializer_class = serializers.RoleSerializer


# LOCAL EMAILS


class LocalEmailUsersView(generics.ListAPIView):
    """Exposes all the aliases of the users that activated the internal address
    """
    serializer_class = serializers.LocalEmailUsersSerializer

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value(
                'local_email_accounts_enabled'):
            return (users.User.objects
                    .filter(local_email_enabled=True))
        else:
            return users.User.objects.none()


# DHCP


class HostMacIpView(generics.ListAPIView):
    """Exposes the associations between hostname, mac address and IPv4 in
    order to build the DHCP lease files.
    """
    serializer_class = serializers.HostMacIpSerializer

    def get_queryset(self):
        return all_active_interfaces()


# Firewall

class SubnetPortsOpenView(generics.ListAPIView):
    queryset = machines.IpType.objects.all()
    serializer_class = serializers.SubnetPortsOpenSerializer


class InterfacePortsOpenView(generics.ListAPIView):
    queryset = machines.Interface.objects.filter(port_lists__isnull=False).distinct()
    serializer_class = serializers.InterfacePortsOpenSerializer


# DNS


class DNSZonesView(generics.ListAPIView):
    """Exposes the detailed information about each extension (hostnames,
    IPs, DNS records, etc.) in order to build the DNS zone files.
    """
    queryset = (machines.Extension.objects
                .prefetch_related('soa')
                .prefetch_related('ns_set').prefetch_related('ns_set__ns')
                .prefetch_related('origin')
                .prefetch_related('mx_set').prefetch_related('mx_set__name')
                .prefetch_related('txt_set')
                .prefetch_related('srv_set').prefetch_related('srv_set__target')
                .all())
    serializer_class = serializers.DNSZonesSerializer


class DNSReverseZonesView(generics.ListAPIView):
    """Exposes the detailed information about each extension (hostnames,
    IPs, DNS records, etc.) in order to build the DNS zone files.
    """
    queryset = (machines.IpType.objects.all())
    serializer_class = serializers.DNSReverseZonesSerializer


# MAILING


class StandardMailingView(views.APIView):
    """Exposes list and details of standard mailings (name and members) in
    order to building the corresponding mailing lists.
    """
    pagination_class = PageSizedPagination
    permission_classes = (ACLPermission,)
    perms_map = {'GET': [users.User.can_view_all]}

    def get(self, request, format=None):
        adherents_data = serializers.MailingMemberSerializer(all_has_access(), many=True).data
        data = [{'name': 'adherents', 'members': adherents_data}]
        paginator = self.pagination_class()
        paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(data)


class ClubMailingView(generics.ListAPIView):
    """Exposes list and details of club mailings (name, members and admins) in
    order to build the corresponding mailing lists.
    """
    queryset = users.Club.objects.all()
    serializer_class = serializers.MailingSerializer


# TOKEN AUTHENTICATION


class ObtainExpiringAuthToken(ObtainAuthToken):
    """Exposes a view to obtain a authentication token.

    This view as the same behavior as the
    `rest_framework.auth_token.views.ObtainAuthToken` view except that the
    expiration time is send along with the token as an addtional information.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        token_duration = datetime.timedelta(
            seconds=settings.API_TOKEN_DURATION
        )
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if not created and token.created < utc_now - token_duration:
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow()
            token.save()

        return Response({
            'token': token.key,
            'expiration': token.created + token_duration
        })


class EMailAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.EMailAddress` objects.
    """
    serializer_class = serializers.EMailAddressSerializer
    queryset = users.EMailAddress.objects.none()

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value(
                'local_email_accounts_enabled'):
            return (users.EMailAddress.objects
                    .filter(user__local_email_enabled=True))
        else:
            return users.EMailAddress.objects.none()
