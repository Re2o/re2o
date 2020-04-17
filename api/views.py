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
from django.contrib.auth.models import Group
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


# COTISATIONS


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects.
    """

    queryset = cotisations.Facture.objects.all()
    serializer_class = serializers.FactureSerializer


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Facture` objects.
    """

    queryset = cotisations.BaseInvoice.objects.all()
    serializer_class = serializers.BaseInvoiceSerializer


class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Vente` objects.
    """

    queryset = cotisations.Vente.objects.all()
    serializer_class = serializers.VenteSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Article` objects.
    """

    queryset = cotisations.Article.objects.all()
    serializer_class = serializers.ArticleSerializer


class BanqueViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Banque` objects.
    """

    queryset = cotisations.Banque.objects.all()
    serializer_class = serializers.BanqueSerializer


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Paiement` objects.
    """

    queryset = cotisations.Paiement.objects.all()
    serializer_class = serializers.PaiementSerializer


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `cotisations.models.Cotisation` objects.
    """

    queryset = cotisations.Cotisation.objects.all()
    serializer_class = serializers.CotisationSerializer


# MACHINES


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Machine` objects.
    """

    queryset = machines.Machine.objects.all()
    serializer_class = serializers.MachineSerializer


class MachineTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.MachineType` objects.
    """

    queryset = machines.MachineType.objects.all()
    serializer_class = serializers.MachineTypeSerializer


class IpTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.IpType` objects.
    """

    queryset = machines.IpType.objects.all()
    serializer_class = serializers.IpTypeSerializer


class VlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Vlan` objects.
    """

    queryset = machines.Vlan.objects.all()
    serializer_class = serializers.VlanSerializer


class NasViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Nas` objects.
    """

    queryset = machines.Nas.objects.all()
    serializer_class = serializers.NasSerializer


class SOAViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.SOA` objects.
    """

    queryset = machines.SOA.objects.all()
    serializer_class = serializers.SOASerializer


class ExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Extension` objects.
    """

    queryset = machines.Extension.objects.all()
    serializer_class = serializers.ExtensionSerializer


class MxViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Mx` objects.
    """

    queryset = machines.Mx.objects.all()
    serializer_class = serializers.MxSerializer


class NsViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Ns` objects.
    """

    queryset = machines.Ns.objects.all()
    serializer_class = serializers.NsSerializer


class TxtViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Txt` objects.
    """

    queryset = machines.Txt.objects.all()
    serializer_class = serializers.TxtSerializer


class DNameViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.DName` objects.
    """

    queryset = machines.DName.objects.all()
    serializer_class = serializers.DNameSerializer


class SrvViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Srv` objects.
    """

    queryset = machines.Srv.objects.all()
    serializer_class = serializers.SrvSerializer


class SshFpViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.SshFp` objects.
    """

    queryset = machines.SshFp.objects.all()
    serializer_class = serializers.SshFpSerializer


class InterfaceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Interface` objects.
    """

    queryset = machines.Interface.objects.all()
    serializer_class = serializers.InterfaceSerializer


class Ipv6ListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Ipv6List` objects.
    """

    queryset = machines.Ipv6List.objects.all()
    serializer_class = serializers.Ipv6ListSerializer


class DomainViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Domain` objects.
    """

    queryset = machines.Domain.objects.all()
    serializer_class = serializers.DomainSerializer


class IpListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.IpList` objects.
    """

    queryset = machines.IpList.objects.all()
    serializer_class = serializers.IpListSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Service` objects.
    """

    queryset = machines.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ServiceLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Service_link` objects.
    """

    queryset = machines.Service_link.objects.all()
    serializer_class = serializers.ServiceLinkSerializer


class OuverturePortListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.OuverturePortList`
    objects.
    """

    queryset = machines.OuverturePortList.objects.all()
    serializer_class = serializers.OuverturePortListSerializer


class OuverturePortViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.OuverturePort` objects.
    """

    queryset = machines.OuverturePort.objects.all()
    serializer_class = serializers.OuverturePortSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Machine` objects.
    """

    queryset = machines.Role.objects.all()
    serializer_class = serializers.RoleSerializer


# PREFERENCES
# Those views differ a bit because there is only one object
# to display, so we don't bother with the listing part


class OptionalUserView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalUser.can_view_all]}
    serializer_class = serializers.OptionalUserSerializer

    def get_object(self):
        return preferences.OptionalUser.objects.first()


class OptionalMachineView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalMachine` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalMachine.can_view_all]}
    serializer_class = serializers.OptionalMachineSerializer

    def get_object(self):
        return preferences.OptionalMachine.objects.first()


class OptionalTopologieView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalTopologie` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalTopologie.can_view_all]}
    serializer_class = serializers.OptionalTopologieSerializer

    def get_object(self):
        return preferences.OptionalTopologie.objects.first()


class RadiusOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalTopologie` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.RadiusOption.can_view_all]}
    serializer_class = serializers.RadiusOptionSerializer

    def get_object(self):
        return preferences.RadiusOption.objects.first()


class GeneralOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.GeneralOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.GeneralOption.can_view_all]}
    serializer_class = serializers.GeneralOptionSerializer

    def get_object(self):
        return preferences.GeneralOption.objects.first()


class HomeServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `preferences.models.Service` objects.
    """

    queryset = preferences.Service.objects.all()
    serializer_class = serializers.HomeServiceSerializer


class AssoOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.AssoOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.AssoOption.can_view_all]}
    serializer_class = serializers.AssoOptionSerializer

    def get_object(self):
        return preferences.AssoOption.objects.first()


class HomeOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.HomeOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.HomeOption.can_view_all]}
    serializer_class = serializers.HomeOptionSerializer

    def get_object(self):
        return preferences.HomeOption.objects.first()


class MailMessageOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.MailMessageOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.MailMessageOption.can_view_all]}
    serializer_class = serializers.MailMessageOptionSerializer

    def get_object(self):
        return preferences.MailMessageOption.objects.first()


# TOPOLOGIE


class StackViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Stack` objects.
    """

    queryset = topologie.Stack.objects.all()
    serializer_class = serializers.StackSerializer


class AccessPointViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.AccessPoint` objects.
    """

    queryset = topologie.AccessPoint.objects.all()
    serializer_class = serializers.AccessPointSerializer


class SwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Switch` objects.
    """

    queryset = topologie.Switch.objects.all()
    serializer_class = serializers.SwitchSerializer


class ServerViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Server` objects.
    """

    queryset = topologie.Server.objects.all()
    serializer_class = serializers.ServerSerializer


class ModelSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.ModelSwitch` objects.
    """

    queryset = topologie.ModelSwitch.objects.all()
    serializer_class = serializers.ModelSwitchSerializer


class ConstructorSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.ConstructorSwitch`
    objects.
    """

    queryset = topologie.ConstructorSwitch.objects.all()
    serializer_class = serializers.ConstructorSwitchSerializer


class SwitchBayViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.SwitchBay` objects.
    """

    queryset = topologie.SwitchBay.objects.all()
    serializer_class = serializers.SwitchBaySerializer


class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Building` objects.
    """

    queryset = topologie.Building.objects.all()
    serializer_class = serializers.BuildingSerializer


class SwitchPortViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Port` objects.
    """

    queryset = topologie.Port.objects.all()
    serializer_class = serializers.SwitchPortSerializer


class PortProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.PortProfile` objects.
    """

    queryset = topologie.PortProfile.objects.all()
    serializer_class = serializers.PortProfileSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Room` objects.
    """

    queryset = topologie.Room.objects.all()
    serializer_class = serializers.RoomSerializer


class PortProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.PortProfile` objects.
    """

    queryset = topologie.PortProfile.objects.all()
    serializer_class = serializers.PortProfileSerializer


# USER


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Users` objects.
    """

    queryset = users.User.objects.all()
    serializer_class = serializers.UserSerializer


class HomeCreationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users` objects to create homes.
    """

    queryset = users.User.objects.exclude(
        Q(state=users.User.STATE_DISABLED)
        | Q(state=users.User.STATE_NOT_YET_ACTIVE)
        | Q(state=users.User.STATE_EMAIL_NOT_YET_CONFIRMED)
        | Q(state=users.User.STATE_FULL_ARCHIVE)
        | Q(state=users.User.STATE_SUSPENDED)
    )
    serializer_class = serializers.BasicUserSerializer


class NormalUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users`without specific rights objects."""

    queryset = users.User.objects.exclude(groups__listright__critical=True).distinct()
    serializer_class = serializers.BasicUserSerializer


class CriticalUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users`without specific rights objects."""

    queryset = users.User.objects.filter(groups__listright__critical=True).distinct()
    serializer_class = serializers.BasicUserSerializer


class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Club` objects.
    """

    queryset = users.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class AdherentViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Adherent` objects.
    """

    queryset = users.Adherent.objects.all()
    serializer_class = serializers.AdherentSerializer


class ServiceUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ServiceUser` objects.
    """

    queryset = users.ServiceUser.objects.all()
    serializer_class = serializers.ServiceUserSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.School` objects.
    """

    queryset = users.School.objects.all()
    serializer_class = serializers.SchoolSerializer


class ListRightViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListRight` objects.
    """

    queryset = users.ListRight.objects.all()
    serializer_class = serializers.ListRightSerializer


class ShellViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListShell` objects.
    """

    queryset = users.ListShell.objects.all()
    serializer_class = serializers.ShellSerializer


class BanViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Ban` objects.
    """

    queryset = users.Ban.objects.all()
    serializer_class = serializers.BanSerializer


class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Whitelist` objects.
    """

    queryset = users.Whitelist.objects.all()
    serializer_class = serializers.WhitelistSerializer


class EMailAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.EMailAddress` objects.
    """

    serializer_class = serializers.EMailAddressSerializer
    queryset = users.EMailAddress.objects.none()

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return users.EMailAddress.objects.filter(user__local_email_enabled=True)
        else:
            return users.EMailAddress.objects.none()


# SERVICE REGEN


class ServiceRegenViewSet(viewsets.ModelViewSet):
    """Exposes list and details of the services to regen
    """

    serializer_class = serializers.ServiceRegenSerializer

    def get_queryset(self):
        queryset = machines.Service_link.objects.select_related(
            "server__domain"
        ).select_related("service")
        if "hostname" in self.request.GET:
            hostname = self.request.GET["hostname"]
            queryset = queryset.filter(server__domain__name__iexact=hostname)
        return queryset


# Config des switches


class SwitchPortView(generics.ListAPIView):
    """Output each port of a switch, to be serialized with
    additionnal informations (profiles etc)
    """

    queryset = (
        topologie.Switch.objects.all()
        .select_related("switchbay")
        .select_related("model__constructor")
        .prefetch_related("ports__custom_profile__vlan_tagged")
        .prefetch_related("ports__custom_profile__vlan_untagged")
        .prefetch_related("ports__machine_interface__domain__extension")
        .prefetch_related("ports__room")
    )

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

    queryset = machines.Role.objects.all().prefetch_related("servers")
    serializer_class = serializers.RoleSerializer


# LOCAL EMAILS


class LocalEmailUsersView(generics.ListAPIView):
    """Exposes all the aliases of the users that activated the internal address
    """

    serializer_class = serializers.LocalEmailUsersSerializer

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return users.User.objects.filter(local_email_enabled=True)
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

    queryset = (
        machines.Extension.objects.prefetch_related("soa")
        .prefetch_related("ns_set")
        .prefetch_related("ns_set__ns")
        .prefetch_related("origin")
        .prefetch_related("mx_set")
        .prefetch_related("mx_set__name")
        .prefetch_related("txt_set")
        .prefetch_related("srv_set")
        .prefetch_related("srv_set__target")
        .all()
    )
    serializer_class = serializers.DNSZonesSerializer


class DNSReverseZonesView(generics.ListAPIView):
    """Exposes the detailed information about each extension (hostnames,
    IPs, DNS records, etc.) in order to build the DNS zone files.
    """

    queryset = machines.IpType.objects.all()
    serializer_class = serializers.DNSReverseZonesSerializer


# MAILING


class StandardMailingView(views.APIView):
    """Exposes list and details of standard mailings (name and members) in
    order to building the corresponding mailing lists.
    """

    pagination_class = PageSizedPagination
    permission_classes = (ACLPermission,)
    perms_map = {"GET": [users.User.can_view_all]}

    def get(self, request, format=None):
        adherents_data = serializers.MailingMemberSerializer(
            all_has_access(), many=True
        ).data
        
        data = [{"name": "adherents", "members": adherents_data}]
        groups = Group.objects.all()
        for group in groups:
            group_data = serializers.MailingMemberSerializer(
                group.user_set.all(), many=True
            ).data
            data.append({"name": group.name, "members": group_data})

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
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        token_duration = datetime.timedelta(seconds=settings.API_TOKEN_DURATION)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if not created and token.created < utc_now - token_duration:
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow()
            token.save()

        return Response(
            {"token": token.key, "expiration": token.created + token_duration}
        )
