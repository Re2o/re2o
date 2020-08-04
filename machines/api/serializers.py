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

import machines.models as machines
from api.serializers import NamespacedHRField, NamespacedHIField, NamespacedHMSerializer


class MachineSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Machine` objects.
    """

    class Meta:
        model = machines.Machine
        fields = ("user", "name", "active", "api_url")


class MachineTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.MachineType` objects.
    """

    class Meta:
        model = machines.MachineType
        fields = ("name", "ip_type", "api_url")


class IpTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpType` objects.
    """

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "extension",
            "need_infra",
            "domaine_ip_start",
            "domaine_ip_stop",
            "prefix_v6",
            "vlan",
            "ouverture_ports",
            "api_url",
        )


class VlanSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Vlan` objects.
    """

    class Meta:
        model = machines.Vlan
        fields = (
            "vlan_id",
            "name",
            "comment",
            "arp_protect",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "igmp",
            "mld",
            "api_url",
        )


class NasSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Nas` objects.
    """

    class Meta:
        model = machines.Nas
        fields = (
            "name",
            "nas_type",
            "machine_type",
            "port_access_mode",
            "autocapture_mac",
            "api_url",
        )


class SOASerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SOA` objects.
    """

    class Meta:
        model = machines.SOA
        fields = ("name", "mail", "refresh", "retry", "expire", "ttl", "api_url")


class ExtensionSerializer(NamespacedHMSerializer):
    """Serialize machines.models.Extension objects.
    """

    class Meta:
        model = machines.Extension
        fields = ("name", "need_infra", "origin", "origin_v6", "soa", "api_url")


class MxSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Mx` objects.
    """

    class Meta:
        model = machines.Mx
        fields = ("zone", "priority", "name", "api_url")


class DNameSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.DName` objects.
    """

    class Meta:
        model = machines.DName
        fields = ("zone", "alias", "api_url")


class NsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ns` objects.
    """

    class Meta:
        model = machines.Ns
        fields = ("zone", "ns", "api_url")


class TxtSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Txt` objects.
    """

    class Meta:
        model = machines.Txt
        fields = ("zone", "field1", "field2", "api_url")


class SrvSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Srv` objects.
    """

    class Meta:
        model = machines.Srv
        fields = (
            "service",
            "protocole",
            "extension",
            "ttl",
            "priority",
            "weight",
            "port",
            "target",
            "api_url",
        )


class SshFpSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SSHFP` objects.
    """

    class Meta:
        model = machines.SshFp
        field = ("machine", "pub_key_entry", "algo", "comment", "api_url")


class InterfaceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Interface` objects.
    """

    mac_address = serializers.CharField()
    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = machines.Interface
        fields = (
            "ipv4",
            "mac_address",
            "machine",
            "machine_type",
            "details",
            "port_lists",
            "active",
            "api_url",
        )


class Ipv6ListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """

    class Meta:
        model = machines.Ipv6List
        fields = ("ipv6", "interface", "slaac_ip", "active", "api_url")


class DomainSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Domain` objects.
    """

    class Meta:
        model = machines.Domain
        fields = ("interface_parent", "name", "extension", "cname", "api_url")


class IpListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpList` objects.
    """

    class Meta:
        model = machines.IpList
        fields = ("ipv4", "ip_type", "need_infra", "api_url")


class ServiceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service` objects.
    """

    class Meta:
        model = machines.Service
        fields = (
            "service_type",
            "min_time_regen",
            "regular_time_regen",
            "servers",
            "api_url",
        )


class ServiceLinkSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service_link` objects.
    """

    class Meta:
        model = machines.Service_link
        fields = (
            "service",
            "server",
            "last_regen",
            "asked_regen",
            "need_regen",
            "api_url",
        )
        extra_kwargs = {"api_url": {"view_name": "servicelink-detail"}}


class OuverturePortListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePortList` objects.
    """

    tcp_ports_in = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    udp_ports_in = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    tcp_ports_out = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    udp_ports_out = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )

    class Meta:
        model = machines.OuverturePortList
        fields = (
            "name",
            "tcp_ports_in",
            "udp_ports_in",
            "tcp_ports_out",
            "udp_ports_out",
            "api_url",
        )


class OuverturePortSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    class Meta:
        model = machines.OuverturePort
        fields = ("begin", "end", "port_list", "protocole", "io", "api_url")


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    servers = InterfaceSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ("role_type", "servers", "api_url")


class ServiceRegenSerializer(NamespacedHMSerializer):
    """Serialize the data about the services to regen.
    """

    hostname = serializers.CharField(source="server.domain.name", read_only=True)
    service_name = serializers.CharField(source="service.service_type", read_only=True)
    need_regen = serializers.BooleanField()

    class Meta:
        model = machines.Service_link
        fields = ("hostname", "service_name", "need_regen", "api_url")
        extra_kwargs = {"api_url": {"view_name": "serviceregen-detail"}}


class HostMacIpSerializer(serializers.ModelSerializer):
    """Serialize the data about the hostname-ipv4-mac address association
    to build the DHCP lease files.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    extension = serializers.CharField(source="domain.extension.name", read_only=True)
    mac_address = serializers.CharField(read_only=True)
    ip_type = serializers.CharField(source="machine_type.ip_type", read_only=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "extension", "mac_address", "ipv4", "ip_type")


class FirewallPortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = machines.OuverturePort
        fields = ("begin", "end", "protocole", "io", "show_port")


class FirewallOuverturePortListSerializer(serializers.ModelSerializer):
    tcp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    tcp_ports_out = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_out = FirewallPortListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.OuverturePortList
        fields = ("tcp_ports_in", "udp_ports_in", "tcp_ports_out", "udp_ports_out")


class SubnetPortsOpenSerializer(serializers.ModelSerializer):
    ouverture_ports = FirewallOuverturePortListSerializer(read_only=True)

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "domaine_ip_start",
            "domaine_ip_stop",
            "complete_prefixv6",
            "ouverture_ports",
        )


class InterfacePortsOpenSerializer(serializers.ModelSerializer):
    port_lists = FirewallOuverturePortListSerializer(read_only=True, many=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("port_lists", "ipv4", "ipv6")


class SOARecordSerializer(SOASerializer):
    """Serialize `machines.models.SOA` objects with the data needed to
    generate a SOA DNS record.
    """

    class Meta:
        model = machines.SOA
        fields = ("name", "mail", "refresh", "retry", "expire", "ttl")


class OriginV4RecordSerializer(IpListSerializer):
    """Serialize `machines.models.IpList` objects with the data needed to
    generate an IPv4 Origin DNS record.
    """

    class Meta(IpListSerializer.Meta):
        fields = ("ipv4",)


class NSRecordSerializer(NsSerializer):
    """Serialize `machines.models.Ns` objects with the data needed to
    generate a NS DNS record.
    """

    target = serializers.CharField(source="ns", read_only=True)

    class Meta(NsSerializer.Meta):
        fields = ("target", "ttl")


class MXRecordSerializer(MxSerializer):
    """Serialize `machines.models.Mx` objects with the data needed to
    generate a MX DNS record.
    """

    target = serializers.CharField(source="name", read_only=True)

    class Meta(MxSerializer.Meta):
        fields = ("target", "priority", "ttl")


class TXTRecordSerializer(TxtSerializer):
    """Serialize `machines.models.Txt` objects with the data needed to
    generate a TXT DNS record.
    """

    class Meta(TxtSerializer.Meta):
        fields = ("field1", "field2", "ttl")


class SRVRecordSerializer(SrvSerializer):
    """Serialize `machines.models.Srv` objects with the data needed to
    generate a SRV DNS record.
    """

    target = serializers.CharField(source="target.name", read_only=True)

    class Meta(SrvSerializer.Meta):
        fields = ("service", "protocole", "ttl", "priority", "weight", "port", "target")


class SSHFPRecordSerializer(SshFpSerializer):
    """Serialize `machines.models.SshFp` objects with the data needed to
    generate a SSHFP DNS record.
    """

    class Meta(SshFpSerializer.Meta):
        fields = ("algo_id", "hash")


class SSHFPInterfaceSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    sshfp = SSHFPRecordSerializer(source="machine.sshfp_set", many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "sshfp")


class ARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a A DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)
    ttl = serializers.IntegerField(source="domain.ttl", read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "ipv4", "ttl")


class AAAARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a AAAA DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)
    ttl = serializers.IntegerField(source="domain.ttl", read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "ipv6", "ttl")


class CNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """

    alias = serializers.CharField(source="cname", read_only=True)
    hostname = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = machines.Domain
        fields = ("alias", "hostname", "ttl")


class DNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a DNAME DNS record.
    """

    alias = serializers.CharField(read_only=True)
    zone = serializers.CharField(read_only=True)

    class Meta:
        model = machines.DName
        fields = ("alias", "zone", "ttl")


class DNSZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """

    soa = SOARecordSerializer()
    ns_records = NSRecordSerializer(many=True, source="ns_set")
    originv4 = OriginV4RecordSerializer(source="origin")
    originv6 = serializers.CharField(source="origin_v6")
    mx_records = MXRecordSerializer(many=True, source="mx_set")
    txt_records = TXTRecordSerializer(many=True, source="txt_set")
    srv_records = SRVRecordSerializer(many=True, source="srv_set")
    a_records = ARecordSerializer(many=True, source="get_associated_a_records")
    aaaa_records = AAAARecordSerializer(many=True, source="get_associated_aaaa_records")
    cname_records = CNAMERecordSerializer(
        many=True, source="get_associated_cname_records"
    )
    dname_records = DNAMERecordSerializer(
        many=True, source="get_associated_dname_records"
    )
    sshfp_records = SSHFPInterfaceSerializer(
        many=True, source="get_associated_sshfp_records"
    )

    class Meta:
        model = machines.Extension
        fields = (
            "name",
            "soa",
            "ns_records",
            "originv4",
            "originv6",
            "mx_records",
            "txt_records",
            "srv_records",
            "a_records",
            "aaaa_records",
            "cname_records",
            "dname_records",
            "sshfp_records",
        )


class DNSReverseZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """

    soa = SOARecordSerializer(source="extension.soa")
    extension = serializers.CharField(source="extension.name", read_only=True)
    cidrs = serializers.ListField(
        child=serializers.CharField(), source="ip_set_cidrs_as_str", read_only=True
    )
    ns_records = NSRecordSerializer(many=True, source="extension.ns_set")
    mx_records = MXRecordSerializer(many=True, source="extension.mx_set")
    txt_records = TXTRecordSerializer(many=True, source="extension.txt_set")
    ptr_records = ARecordSerializer(many=True, source="get_associated_ptr_records")
    ptr_v6_records = AAAARecordSerializer(
        many=True, source="get_associated_ptr_v6_records"
    )

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "extension",
            "soa",
            "ns_records",
            "mx_records",
            "txt_records",
            "ptr_records",
            "ptr_v6_records",
            "cidrs",
            "prefix_v6",
            "prefix_v6_length",
        )
