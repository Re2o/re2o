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

from rest_framework import serializers

from re2o.serializers import NamespacedHRField, NamespacedHIField, NamespacedHMSerializer

import machines.models as machines

class MachineSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Machine` objects.
    """

    class Meta:
        model = machines.Machine
        fields = ('user', 'name', 'active', 'api_url')


class MachineTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.MachineType` objects.
    """

    class Meta:
        model = machines.MachineType
        fields = ('type', 'ip_type', 'api_url')


class IpTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpType` objects.
    """

    class Meta:
        model = machines.IpType
        fields = ('type', 'extension', 'need_infra', 'domaine_ip_start',
                  'domaine_ip_stop', 'prefix_v6', 'vlan', 'ouverture_ports',
                  'api_url')


class VlanSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Vlan` objects.
    """

    class Meta:
        model = machines.Vlan
        fields = ('vlan_id', 'name', 'comment', 'arp_protect', 'dhcp_snooping',
                  'dhcpv6_snooping', 'igmp', 'mld', 'api_url')


class NasSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Nas` objects.
    """

    class Meta:
        model = machines.Nas
        fields = ('name', 'nas_type', 'machine_type', 'port_access_mode',
                  'autocapture_mac', 'api_url')


class SOASerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SOA` objects.
    """

    class Meta:
        model = machines.SOA
        fields = ('name', 'mail', 'refresh', 'retry', 'expire', 'ttl',
                  'api_url')


class ExtensionSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Extension` objects.
    """

    class Meta:
        model = machines.Extension
        fields = ('name', 'need_infra', 'origin', 'origin_v6', 'soa',
                  'api_url')


class MxSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Mx` objects.
    """

    class Meta:
        model = machines.Mx
        fields = ('zone', 'priority', 'name', 'api_url')


class DNameSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.DName` objects.
    """

    class Meta:
        model = machines.DName
        fields = ('zone', 'alias', 'api_url')


class NsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ns` objects.
    """

    class Meta:
        model = machines.Ns
        fields = ('zone', 'ns', 'api_url')


class TxtSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Txt` objects.
    """

    class Meta:
        model = machines.Txt
        fields = ('zone', 'field1', 'field2', 'api_url')


class SrvSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Srv` objects.
    """

    class Meta:
        model = machines.Srv
        fields = ('service', 'protocole', 'extension', 'ttl', 'priority',
                  'weight', 'port', 'target', 'api_url')


class SshFpSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SSHFP` objects.
    """

    class Meta:
        model = machines.SshFp
        field = ('machine', 'pub_key_entry', 'algo', 'comment', 'api_url')


class InterfaceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Interface` objects.
    """
    mac_address = serializers.CharField()
    active = serializers.BooleanField(source='is_active')

    class Meta:
        model = machines.Interface
        fields = ('ipv4', 'mac_address', 'machine', 'type', 'details',
                  'port_lists', 'active', 'api_url')


class Ipv6ListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """

    class Meta:
        model = machines.Ipv6List
        fields = ('ipv6', 'interface', 'slaac_ip', 'api_url')


class DomainSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Domain` objects.
    """

    class Meta:
        model = machines.Domain
        fields = ('interface_parent', 'name', 'extension', 'cname',
                  'api_url')


class IpListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpList` objects.
    """

    class Meta:
        model = machines.IpList
        fields = ('ipv4', 'ip_type', 'need_infra', 'api_url')


class ServiceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service` objects.
    """

    class Meta:
        model = machines.Service
        fields = ('service_type', 'min_time_regen', 'regular_time_regen',
                  'servers', 'api_url')


class ServiceLinkSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service_link` objects.
    """

    class Meta:
        model = machines.Service_link
        fields = ('service', 'server', 'last_regen', 'asked_regen',
                  'need_regen', 'api_url')
        extra_kwargs = {
            'api_url': {'view_name': 'servicelink-detail'}
        }


class OuverturePortListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePortList` objects.
    """
    tcp_ports_in = NamespacedHRField(view_name='ouvertureport-detail', many=True, read_only=True)
    udp_ports_in = NamespacedHRField(view_name='ouvertureport-detail', many=True, read_only=True)
    tcp_ports_out = NamespacedHRField(view_name='ouvertureport-detail', many=True, read_only=True)
    udp_ports_out = NamespacedHRField(view_name='ouvertureport-detail', many=True, read_only=True)

    class Meta:
        model = machines.OuverturePortList
        fields = ('name', 'tcp_ports_in', 'udp_ports_in', 'tcp_ports_out',
                  'udp_ports_out', 'api_url')


class OuverturePortSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    class Meta:
        model = machines.OuverturePort
        fields = ('begin', 'end', 'port_list', 'protocole', 'io', 'api_url')


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """
    servers = InterfaceSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ('role_type', 'servers', 'api_url')
