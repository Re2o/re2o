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

"""api.views

The views for the API app. They should all return JSON data and not fallback on
HTML pages such as the login and index pages for a better integration.
"""

import datetime

from django.conf import settings

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, generics

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users

from re2o.utils import all_active_interfaces

from . import serializers


# COTISATIONS APP


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Facture.objects.all()
    serializer_class = serializers.FactureSerializer


class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Vente.objects.all()
    serializer_class = serializers.VenteSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Article.objects.all()
    serializer_class = serializers.ArticleSerializer


class BanqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Banque.objects.all()
    serializer_class = serializers.BanqueSerializer


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Paiement.objects.all()
    serializer_class = serializers.PaiementSerializer


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = cotisations.Cotisation.objects.all()
    serializer_class = serializers.CotisationSerializer


# MACHINES APP


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Machine.objects.all()
    serializer_class = serializers.MachineSerializer


class MachineTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.MachineType.objects.all()
    serializer_class = serializers.MachineTypeSerializer


class IpTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.IpType.objects.all()
    serializer_class = serializers.IpTypeSerializer


class VlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Vlan.objects.all()
    serializer_class = serializers.VlanSerializer


class NasViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Nas.objects.all()
    serializer_class = serializers.NasSerializer


class SOAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.SOA.objects.all()
    serializer_class = serializers.SOASerializer


class ExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Extension.objects.all()
    serializer_class = serializers.ExtensionSerializer


class MxViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Mx.objects.all()
    serializer_class = serializers.MxSerializer


class NsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Ns.objects.all()
    serializer_class = serializers.NsSerializer


class TxtViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Txt.objects.all()
    serializer_class = serializers.TxtSerializer


class SrvViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Srv.objects.all()
    serializer_class = serializers.SrvSerializer


class InterfaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Interface.objects.all()
    serializer_class = serializers.InterfaceSerializer


class Ipv6ListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Ipv6List.objects.all()
    serializer_class = serializers.Ipv6ListSerializer


class DomainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Domain.objects.all()
    serializer_class = serializers.DomainSerializer


class IpListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.IpList.objects.all()
    serializer_class = serializers.IpListSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ServiceLinkViewSet(viewsets.ModelViewSet):
    queryset = machines.Service_link.objects.all()
    serializer_class = serializers.ServiceLinkSerializer


class OuverturePortListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.OuverturePortList.objects.all()
    serializer_class = serializers.OuverturePortListSerializer


class OuverturePortViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.OuverturePort.objects.all()
    serializer_class = serializers.OuverturePortSerializer


# PREFERENCES APP

# class OptionalUserViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.OptionalUser.objects.all()
#     serializer_class = serializers.OptionalUserSerializer
# 
# 
# class OptionalMachineViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.OptionalMachine.objects.all()
#     serializer_class = serializers.OptionalMachineSerializer
# 
# 
# class OptionalTopologieViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.OptionalTopologie.objects.all()
#     serializer_class = serializers.OptionalTopologieSerializer
# 
# 
# class GeneralOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.GeneralOption.objects.all()
#     serializer_class = serializers.GeneralOptionSerializer
# 
# 
# class ServiceOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.ServiceOption.objects.all()
#     serializer_class = serializers.ServiceOptionSerializer
# 
# 
# class AssoOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.AssoOption.objects.all()
#     serializer_class = serializers.AssoOptionSerializer
# 
# 
# class HomeOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.HomeOption.objects.all()
#     serializer_class = serializers.HomeOptionSerializer
# 
# 
# class MailMessageOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = preferences.MailMessageOption.objects.all()
#     serializer_class = serializers.MailMessageOptionSerializer


# TOPOLOGIE APP


class StackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.Stack.objects.all()
    serializer_class = serializers.StackSerializer


class AccessPointViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.AccessPoint.objects.all()
    serializer_class = serializers.AccessPointSerializer


class SwitchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.Switch.objects.all()
    serializer_class = serializers.SwitchSerializer


class ModelSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.ModelSwitch.objects.all()
    serializer_class = serializers.ModelSwitchSerializer


class ConstructorSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.ConstructorSwitch.objects.all()
    serializer_class = serializers.ConstructorSwitchSerializer


class SwitchBayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.SwitchBay.objects.all()
    serializer_class = serializers.SwitchBaySerializer


class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.Building.objects.all()
    serializer_class = serializers.BuildingSerializer


class SwitchPortViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.Port.objects.all()
    serializer_class = serializers.SwitchPortSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = topologie.Room.objects.all()
    serializer_class = serializers.RoomSerializer


# USER APP


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.User.objects.all()
    serializer_class = serializers.UserSerializer


class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class AdherentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.Adherent.objects.all()
    serializer_class = serializers.AdherentSerializer


class ServiceUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.ServiceUser.objects.all()
    serializer_class = serializers.ServiceUserSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.School.objects.all()
    serializer_class = serializers.SchoolSerializer


class ListRightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.ListRight.objects.all()
    serializer_class = serializers.ListRightSerializer


class ShellViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.ListShell.objects.all()
    serializer_class = serializers.ShellSerializer


class BanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.Ban.objects.all()
    serializer_class = serializers.BanSerializer


class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = users.Whitelist.objects.all()
    serializer_class = serializers.WhitelistSerializer


# Services views


class ServiceRegenView(generics.ListAPIView):
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


# DHCP views

class HostMacIpView(generics.ListAPIView):
    queryset = all_active_interfaces()
    serializer_class = serializers.HostMacIpSerializer


# DNS views

class DNSZonesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = machines.Extension.objects.all()
    serializer_class = serializers.DNSZonesSerializer


# Subclass the standard rest_framework.auth_token.views.ObtainAuthToken
# in order to renew the lease of the token and add expiration time
class ObtainExpiringAuthToken(ObtainAuthToken):
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
