# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019 Arthur Grisel-Davy
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

from rest_framework import viewsets, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

import machines.models as machines

from . import serializers
from api.pagination import PageSizedPagination
from api.permissions import ACLPermission

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
