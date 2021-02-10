# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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

from rest_framework import generics, viewsets

import machines.models as machines
from re2o.utils import all_active_interfaces

from . import serializers


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Machine` objects."""

    queryset = machines.Machine.objects.all()
    serializer_class = serializers.MachineSerializer


class MachineTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.MachineType` objects."""

    queryset = machines.MachineType.objects.all()
    serializer_class = serializers.MachineTypeSerializer


class IpTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.IpType` objects."""

    queryset = machines.IpType.objects.all()
    serializer_class = serializers.IpTypeSerializer


class VlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Vlan` objects."""

    queryset = machines.Vlan.objects.all()
    serializer_class = serializers.VlanSerializer


class NasViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Nas` objects."""

    queryset = machines.Nas.objects.all()
    serializer_class = serializers.NasSerializer


class SOAViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.SOA` objects."""

    queryset = machines.SOA.objects.all()
    serializer_class = serializers.SOASerializer


class ExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Extension` objects."""

    queryset = machines.Extension.objects.all()
    serializer_class = serializers.ExtensionSerializer


class MxViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Mx` objects."""

    queryset = machines.Mx.objects.all()
    serializer_class = serializers.MxSerializer


class NsViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Ns` objects."""

    queryset = machines.Ns.objects.all()
    serializer_class = serializers.NsSerializer


class TxtViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Txt` objects."""

    queryset = machines.Txt.objects.all()
    serializer_class = serializers.TxtSerializer


class DNameViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.DName` objects."""

    queryset = machines.DName.objects.all()
    serializer_class = serializers.DNameSerializer


class SrvViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Srv` objects."""

    queryset = machines.Srv.objects.all()
    serializer_class = serializers.SrvSerializer


class SshFpViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.SshFp` objects."""

    queryset = machines.SshFp.objects.all()
    serializer_class = serializers.SshFpSerializer


class InterfaceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Interface` objects."""

    queryset = machines.Interface.objects.all()
    serializer_class = serializers.InterfaceSerializer


class Ipv6ListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Ipv6List` objects."""

    queryset = machines.Ipv6List.objects.all()
    serializer_class = serializers.Ipv6ListSerializer


class DomainViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Domain` objects."""

    queryset = machines.Domain.objects.all()
    serializer_class = serializers.DomainSerializer


class IpListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.IpList` objects."""

    queryset = machines.IpList.objects.all()
    serializer_class = serializers.IpListSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Service` objects."""

    queryset = machines.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ServiceLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Service_link` objects."""

    queryset = machines.Service_link.objects.all()
    serializer_class = serializers.ServiceLinkSerializer


class OuverturePortListViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.OuverturePortList`
    objects.
    """

    queryset = machines.OuverturePortList.objects.all()
    serializer_class = serializers.OuverturePortListSerializer


class OuverturePortViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.OuverturePort` objects."""

    queryset = machines.OuverturePort.objects.all()
    serializer_class = serializers.OuverturePortSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `machines.models.Machine` objects."""

    queryset = machines.Role.objects.all()
    serializer_class = serializers.RoleSerializer


class ServiceRegenViewSet(viewsets.ModelViewSet):
    """Exposes list and details of the services to regen"""

    serializer_class = serializers.ServiceRegenSerializer

    def get_queryset(self):
        queryset = machines.Service_link.objects.select_related(
            "server__domain"
        ).select_related("service")
        if "hostname" in self.request.GET:
            hostname = self.request.GET["hostname"]
            queryset = queryset.filter(server__domain__name__iexact=hostname)
        return queryset


class HostMacIpView(generics.ListAPIView):
    """Exposes the associations between hostname, mac address and IPv4 in
    order to build the DHCP lease files.
    """

    serializer_class = serializers.HostMacIpSerializer

    def get_queryset(self):
        return all_active_interfaces()


class SubnetPortsOpenView(generics.ListAPIView):
    queryset = machines.IpType.objects.all()
    serializer_class = serializers.SubnetPortsOpenSerializer


class InterfacePortsOpenView(generics.ListAPIView):
    queryset = machines.Interface.objects.filter(port_lists__isnull=False).distinct()
    serializer_class = serializers.InterfacePortsOpenSerializer


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
