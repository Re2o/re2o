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

"""Defines the serializers of the API
"""

from rest_framework import serializers

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users

from re2o.serializers import NamespacedHRField, NamespacedHIField, NamespacedHMSerializer

from machines.api.serializers import (
    VlanSerializer,
    Ipv6ListSerializer,
    SOASerializer,
    IpListSerializer,
    NsSerializer,
    MxSerializer,
    TxtSerializer,
    SrvSerializer,
    SshFpSerializer,
)

from users.api.serializers import (
    UserSerializer,
    ClubSerializer,
    EMailAddressSerializer
)


# CONF SWITCH

class InterfaceVlanSerializer(NamespacedHMSerializer):
    domain = serializers.CharField(read_only=True)
    ipv4 = serializers.CharField(read_only=True)
    ipv6 = Ipv6ListSerializer(read_only=True, many=True)
    vlan_id = serializers.IntegerField(source='type.ip_type.vlan.vlan_id', read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('ipv4', 'ipv6', 'domain', 'vlan_id')

class InterfaceRoleSerializer(NamespacedHMSerializer):
    interface = InterfaceVlanSerializer(source='machine.interface_set', read_only=True, many=True)

    class Meta:
        model = machines.Interface
        fields = ('interface',)


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """
    servers = InterfaceRoleSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ('role_type', 'servers', 'specific_role')


class VlanPortSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Vlan
        fields = ('vlan_id', 'name')


class ProfilSerializer(NamespacedHMSerializer):
    vlan_untagged = VlanSerializer(read_only=True)
    vlan_tagged = VlanPortSerializer(read_only=True, many=True)

    class Meta:
        model = topologie.PortProfile
        fields = ('name', 'profil_default', 'vlan_untagged', 'vlan_tagged', 'radius_type', 'radius_mode', 'speed', 'mac_limit', 'flow_control', 'dhcp_snooping', 'dhcpv6_snooping', 'arp_protect', 'ra_guard', 'loop_protect', 'vlan_untagged', 'vlan_tagged')


class ModelSwitchSerializer(NamespacedHMSerializer):
    constructor = serializers.CharField(read_only=True)

    class Meta:
        model = topologie.ModelSwitch
        fields = ('reference', 'firmware', 'constructor')


class SwitchBaySerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.SwitchBay
        fields = ('name',)


class PortsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """
    get_port_profile = ProfilSerializer(read_only=True)


    class Meta:
        model = topologie.Port
        fields = ('state', 'port', 'pretty_name', 'get_port_profile')



class SwitchPortSerializer(serializers.ModelSerializer):
    """Serialize the data about the switches"""
    ports = PortsSerializer(many=True, read_only=True)
    model = ModelSwitchSerializer(read_only=True)
    switchbay = SwitchBaySerializer(read_only=True)


    class Meta:
        model = topologie.Switch
        fields = ('short_name', 'model', 'switchbay', 'ports', 'ipv4', 'ipv6',
                  'interfaces_subnet', 'interfaces6_subnet', 'automatic_provision', 'rest_enabled',
                  'web_management_enabled', 'get_radius_key_value', 'get_management_cred_value',
                  'list_modules')

# SERVICE REGEN


class ServiceRegenSerializer(NamespacedHMSerializer):
    """Serialize the data about the services to regen.
    """
    hostname = serializers.CharField(source='server.domain.name', read_only=True)
    service_name = serializers.CharField(source='service.service_type', read_only=True)
    need_regen = serializers.BooleanField()

    class Meta:
        model = machines.Service_link
        fields = ('hostname', 'service_name', 'need_regen', 'api_url')
        extra_kwargs = {
            'api_url': {'view_name': 'serviceregen-detail'}
        }


# Firewall

class FirewallPortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = machines.OuverturePort
        fields = ('begin', 'end', 'protocole', 'io', 'show_port')


class FirewallOuverturePortListSerializer(serializers.ModelSerializer):
    tcp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    tcp_ports_out = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_out = FirewallPortListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.OuverturePortList
        fields = ('tcp_ports_in', 'udp_ports_in', 'tcp_ports_out', 'udp_ports_out')


class SubnetPortsOpenSerializer(serializers.ModelSerializer):
    ouverture_ports = FirewallOuverturePortListSerializer(read_only=True)

    class Meta:
        model = machines.IpType
        fields = ('type', 'domaine_ip_start', 'domaine_ip_stop', 'complete_prefixv6', 'ouverture_ports')


class InterfacePortsOpenSerializer(serializers.ModelSerializer):
    port_lists = FirewallOuverturePortListSerializer(read_only=True, many=True)
    ipv4 = serializers.CharField(source='ipv4.ipv4', read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('port_lists', 'ipv4', 'ipv6')


# DHCP


class HostMacIpSerializer(serializers.ModelSerializer):
    """Serialize the data about the hostname-ipv4-mac address association
    to build the DHCP lease files.
    """
    hostname = serializers.CharField(source='domain.name', read_only=True)
    extension = serializers.CharField(source='domain.extension.name', read_only=True)
    mac_address = serializers.CharField(read_only=True)
    ipv4 = serializers.CharField(source='ipv4.ipv4', read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'extension', 'mac_address', 'ipv4')


# DNS


class SOARecordSerializer(SOASerializer):
    """Serialize `machines.models.SOA` objects with the data needed to
    generate a SOA DNS record.
    """

    class Meta:
        model = machines.SOA
        fields = ('name', 'mail', 'refresh', 'retry', 'expire', 'ttl')


class OriginV4RecordSerializer(IpListSerializer):
    """Serialize `machines.models.IpList` objects with the data needed to
    generate an IPv4 Origin DNS record.
    """

    class Meta(IpListSerializer.Meta):
        fields = ('ipv4',)


class NSRecordSerializer(NsSerializer):
    """Serialize `machines.models.Ns` objects with the data needed to
    generate a NS DNS record.
    """
    target = serializers.CharField(source='ns', read_only=True)

    class Meta(NsSerializer.Meta):
        fields = ('target',)


class MXRecordSerializer(MxSerializer):
    """Serialize `machines.models.Mx` objects with the data needed to
    generate a MX DNS record.
    """
    target = serializers.CharField(source='name', read_only=True)

    class Meta(MxSerializer.Meta):
        fields = ('target', 'priority')


class TXTRecordSerializer(TxtSerializer):
    """Serialize `machines.models.Txt` objects with the data needed to
    generate a TXT DNS record.
    """

    class Meta(TxtSerializer.Meta):
        fields = ('field1', 'field2')


class SRVRecordSerializer(SrvSerializer):
    """Serialize `machines.models.Srv` objects with the data needed to
    generate a SRV DNS record.
    """
    target = serializers.CharField(source='target.name', read_only=True)

    class Meta(SrvSerializer.Meta):
        fields = ('service', 'protocole', 'ttl', 'priority', 'weight', 'port', 'target')


class SSHFPRecordSerializer(SshFpSerializer):
    """Serialize `machines.models.SshFp` objects with the data needed to
    generate a SSHFP DNS record.
    """

    class Meta(SshFpSerializer.Meta):
        fields = ('algo_id', 'hash')


class SSHFPInterfaceSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """
    hostname = serializers.CharField(source='domain.name', read_only=True)
    sshfp = SSHFPRecordSerializer(source='machine.sshfp_set', many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'sshfp')


class ARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a A DNS record.
    """
    hostname = serializers.CharField(source='domain.name', read_only=True)
    ipv4 = serializers.CharField(source='ipv4.ipv4', read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'ipv4')


class AAAARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a AAAA DNS record.
    """
    hostname = serializers.CharField(source='domain.name', read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'ipv6')


class CNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """
    alias = serializers.CharField(source='cname', read_only=True)
    hostname = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = machines.Domain
        fields = ('alias', 'hostname')

class DNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a DNAME DNS record.
    """
    alias = serializers.CharField(read_only=True)
    zone = serializers.CharField(read_only=True)

    class Meta:
        model = machines.DName
        fields = ('alias', 'zone')


class DNSZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """
    soa = SOARecordSerializer()
    ns_records = NSRecordSerializer(many=True, source='ns_set')
    originv4 = OriginV4RecordSerializer(source='origin')
    originv6 = serializers.CharField(source='origin_v6')
    mx_records = MXRecordSerializer(many=True, source='mx_set')
    txt_records = TXTRecordSerializer(many=True, source='txt_set')
    srv_records = SRVRecordSerializer(many=True, source='srv_set')
    a_records = ARecordSerializer(many=True, source='get_associated_a_records')
    aaaa_records = AAAARecordSerializer(many=True, source='get_associated_aaaa_records')
    cname_records = CNAMERecordSerializer(many=True, source='get_associated_cname_records')
    dname_records = DNAMERecordSerializer(many=True, source='get_associated_dname_records')
    sshfp_records = SSHFPInterfaceSerializer(many=True, source='get_associated_sshfp_records')

    class Meta:
        model = machines.Extension
        fields = ('name', 'soa', 'ns_records', 'originv4', 'originv6',
                  'mx_records', 'txt_records', 'srv_records', 'a_records',
                  'aaaa_records', 'cname_records', 'dname_records', 'sshfp_records')
#REMINDER


class ReminderUsersSerializer(UserSerializer):
    """Serialize the data about a mailing member.
    """
    class Meta(UserSerializer.Meta):
        fields = ('get_full_name', 'get_mail')


class ReminderSerializer(serializers.ModelSerializer):
    """
    Serialize the data about a reminder
    """
    users_to_remind = ReminderUsersSerializer(many=True)

    class Meta:
        model = preferences.Reminder
        fields = ('days','message','users_to_remind')


class DNSReverseZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """
    soa = SOARecordSerializer(source='extension.soa')
    extension = serializers.CharField(source='extension.name', read_only=True)
    cidrs = serializers.ListField(child=serializers.CharField(), source='ip_set_cidrs_as_str', read_only=True)
    ns_records = NSRecordSerializer(many=True, source='extension.ns_set')
    mx_records = MXRecordSerializer(many=True, source='extension.mx_set')
    txt_records = TXTRecordSerializer(many=True, source='extension.txt_set')
    ptr_records = ARecordSerializer(many=True, source='get_associated_ptr_records')
    ptr_v6_records = AAAARecordSerializer(many=True, source='get_associated_ptr_v6_records')

    class Meta:
        model = machines.IpType
        fields = ('type', 'extension', 'soa', 'ns_records', 'mx_records',
                  'txt_records', 'ptr_records', 'ptr_v6_records', 'cidrs',
                  'prefix_v6', 'prefix_v6_length')


# MAILING


class MailingMemberSerializer(UserSerializer):
    """Serialize the data about a mailing member.
    """

    class Meta(UserSerializer.Meta):
        fields = ('name', 'pseudo', 'get_mail')


class MailingSerializer(ClubSerializer):
    """Serialize the data about a mailing.
    """
    members = MailingMemberSerializer(many=True)
    admins = MailingMemberSerializer(source='administrators', many=True)

    class Meta(ClubSerializer.Meta):
        fields = ('name', 'members', 'admins')


# LOCAL EMAILS


class LocalEmailUsersSerializer(NamespacedHMSerializer):
    email_address = EMailAddressSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = users.User
        fields = ('local_email_enabled', 'local_email_redirect',
                  'email_address', 'email')
