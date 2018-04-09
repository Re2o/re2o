# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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

#Augustin Lemesle

from rest_framework import serializers
from machines.models import (
    Interface,
    IpType,
    Extension,
    IpList,
    MachineType,
    Domain,
    Txt,
    Mx,
    Srv,
    Service_link,
    Ns,
    OuverturePortList,
    OuverturePort,
    Ipv6List
)


class IpTypeField(serializers.RelatedField):
    """Serialisation d'une iptype, renvoie son evaluation str"""
    def to_representation(self, value):
        return value.type


class IpListSerializer(serializers.ModelSerializer):
    """Serialisation d'une iplist, ip_type etant une foreign_key,
    on evalue sa methode str"""
    ip_type = IpTypeField(read_only=True)

    class Meta:
        model = IpList
        fields = ('ipv4', 'ip_type')


class Ipv6ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ipv6List
        fields = ('ipv6', 'slaac_ip')


class InterfaceSerializer(serializers.ModelSerializer):
    """Serialisation d'une interface, ipv4, domain et extension sont
    des foreign_key, on les override et on les evalue avec des fonctions
    get_..."""
    ipv4 = IpListSerializer(read_only=True)
    mac_address = serializers.SerializerMethodField('get_macaddress')
    domain = serializers.SerializerMethodField('get_dns')
    extension = serializers.SerializerMethodField('get_interface_extension')

    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address', 'domain', 'extension')

    def get_dns(self, obj):
        return obj.domain.name

    def get_interface_extension(self, obj):
        return obj.domain.extension.name

    def get_macaddress(self, obj):
        return str(obj.mac_address)


class FullInterfaceSerializer(serializers.ModelSerializer):
    """Serialisation complete d'une interface avec les ipv6 en plus"""
    ipv4 = IpListSerializer(read_only=True)
    ipv6 = Ipv6ListSerializer(read_only=True, many=True)
    mac_address = serializers.SerializerMethodField('get_macaddress')
    domain = serializers.SerializerMethodField('get_dns')
    extension = serializers.SerializerMethodField('get_interface_extension')

    class Meta:
        model = Interface
        fields = ('ipv4', 'ipv6', 'mac_address', 'domain', 'extension')

    def get_dns(self, obj):
        return obj.domain.name

    def get_interface_extension(self, obj):
        return obj.domain.extension.name

    def get_macaddress(self, obj):
        return str(obj.mac_address)


class ExtensionNameField(serializers.RelatedField):
    """Evaluation str d'un objet extension (.example.org)"""
    def to_representation(self, value):
        return value.name


class TypeSerializer(serializers.ModelSerializer):
    """Serialisation d'un iptype : extension et la liste des
    ouvertures de port son evalués en get_... etant des
    foreign_key ou des relations manytomany"""
    extension = ExtensionNameField(read_only=True)
    ouverture_ports_tcp_in = serializers\
        .SerializerMethodField('get_port_policy_input_tcp')
    ouverture_ports_tcp_out = serializers\
        .SerializerMethodField('get_port_policy_output_tcp')
    ouverture_ports_udp_in = serializers\
        .SerializerMethodField('get_port_policy_input_udp')
    ouverture_ports_udp_out = serializers\
        .SerializerMethodField('get_port_policy_output_udp')

    class Meta:
        model = IpType
        fields = ('type', 'extension', 'domaine_ip_start', 'domaine_ip_stop',
                  'prefix_v6',
                  'ouverture_ports_tcp_in', 'ouverture_ports_tcp_out',
                  'ouverture_ports_udp_in', 'ouverture_ports_udp_out',)

    def get_port_policy(self, obj, protocole, io):
        if obj.ouverture_ports is None:
            return []
        return map(
            str,
            obj.ouverture_ports.ouvertureport_set.filter(
                protocole=protocole
            ).filter(io=io)
        )

    def get_port_policy_input_tcp(self, obj):
        """Renvoie la liste des ports ouverts en entrée tcp"""
        return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.IN)

    def get_port_policy_output_tcp(self, obj):
        """Renvoie la liste des ports ouverts en sortie tcp"""
        return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.OUT)

    def get_port_policy_input_udp(self, obj):
        """Renvoie la liste des ports ouverts en entrée udp"""
        return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.IN)

    def get_port_policy_output_udp(self, obj):
        """Renvoie la liste des ports ouverts en sortie udp"""
        return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.OUT)


class ExtensionSerializer(serializers.ModelSerializer):
    """Serialisation d'une extension : origin_ip et la zone sont
    des foreign_key donc evalués en get_..."""
    origin = serializers.SerializerMethodField('get_origin_ip')
    zone_entry = serializers.SerializerMethodField('get_zone_name')
    soa = serializers.SerializerMethodField('get_soa_data')

    class Meta:
        model = Extension
        fields = ('name', 'origin', 'origin_v6', 'zone_entry', 'soa')

    def get_origin_ip(self, obj):
        return getattr(obj.origin, 'ipv4', None)

    def get_zone_name(self, obj):
        return str(obj.dns_entry)

    def get_soa_data(self, obj):
        return { 'mail': obj.soa.dns_soa_mail, 'param': obj.soa.dns_soa_param }


class MxSerializer(serializers.ModelSerializer):
    """Serialisation d'un MX, evaluation du nom, de la zone
    et du serveur cible, etant des foreign_key"""
    name = serializers.SerializerMethodField('get_entry_name')
    zone = serializers.SerializerMethodField('get_zone_name')
    mx_entry = serializers.SerializerMethodField('get_mx_name')

    class Meta:
        model = Mx
        fields = ('zone', 'priority', 'name', 'mx_entry')

    def get_entry_name(self, obj):
        return str(obj.name)

    def get_zone_name(self, obj):
        return obj.zone.name

    def get_mx_name(self, obj):
        return str(obj.dns_entry)


class TxtSerializer(serializers.ModelSerializer):
    """Serialisation d'un txt : zone cible et l'entrée txt
    sont evaluées à part"""
    zone = serializers.SerializerMethodField('get_zone_name')
    txt_entry = serializers.SerializerMethodField('get_txt_name')

    class Meta:
        model = Txt
        fields = ('zone', 'txt_entry', 'field1', 'field2')

    def get_zone_name(self, obj):
        return str(obj.zone.name)

    def get_txt_name(self, obj):
        return str(obj.dns_entry)


class SrvSerializer(serializers.ModelSerializer):
    """Serialisation d'un srv : zone cible et l'entrée txt"""
    extension = serializers.SerializerMethodField('get_extension_name')
    srv_entry = serializers.SerializerMethodField('get_srv_name')

    class Meta:
        model = Srv
        fields = (
            'service',
            'protocole',
            'extension',
            'ttl',
            'priority',
            'weight',
            'port',
            'target',
            'srv_entry'
        )

    def get_extension_name(self, obj):
        return str(obj.extension.name)

    def get_srv_name(self, obj):
        return str(obj.dns_entry)


class NsSerializer(serializers.ModelSerializer):
    """Serialisation d'un NS : la zone, l'entrée ns complète et le serveur
    ns sont évalués à part"""
    zone = serializers.SerializerMethodField('get_zone_name')
    ns = serializers.SerializerMethodField('get_domain_name')
    ns_entry = serializers.SerializerMethodField('get_text_name')

    class Meta:
        model = Ns
        fields = ('zone', 'ns', 'ns_entry')

    def get_zone_name(self, obj):
        return obj.zone.name

    def get_domain_name(self, obj):
        return str(obj.ns)

    def get_text_name(self, obj):
        return str(obj.dns_entry)


class DomainSerializer(serializers.ModelSerializer):
    """Serialisation d'un domain, extension, cname sont des foreign_key,
    et l'entrée complète, sont évalués à part"""
    extension = serializers.SerializerMethodField('get_zone_name')
    cname = serializers.SerializerMethodField('get_alias_name')
    cname_entry = serializers.SerializerMethodField('get_cname_name')

    class Meta:
        model = Domain
        fields = ('name', 'extension', 'cname', 'cname_entry')

    def get_zone_name(self, obj):
        return obj.extension.name

    def get_alias_name(self, obj):
        return str(obj.cname)

    def get_cname_name(self, obj):
        return str(obj.dns_entry)


class ServiceServersSerializer(serializers.ModelSerializer):
    """Evaluation d'un Service, et serialisation"""
    server = serializers.SerializerMethodField('get_server_name')
    service = serializers.SerializerMethodField('get_service_name')
    need_regen = serializers.SerializerMethodField('get_regen_status')

    class Meta:
        model = Service_link
        fields = ('server', 'service', 'need_regen')

    def get_server_name(self, obj):
        return str(obj.server.domain.name)

    def get_service_name(self, obj):
        return str(obj.service)

    def get_regen_status(self, obj):
        return obj.need_regen()


class OuverturePortsSerializer(serializers.Serializer):
    """Serialisation de l'ouverture des ports"""
    ipv4 = serializers.SerializerMethodField()
    ipv6 = serializers.SerializerMethodField()

    def get_ipv4():
        return {i.ipv4.ipv4:
            {
                "tcp_in":[j.tcp_ports_in() for j in i.port_lists.all()],
                "tcp_out":[j.tcp_ports_out()for j in i.port_lists.all()],
                "udp_in":[j.udp_ports_in() for j in i.port_lists.all()],
                "udp_out":[j.udp_ports_out() for j in i.port_lists.all()],
            }
                for i in Interface.objects.all() if i.ipv4
        }

    def get_ipv6():
        return {i.ipv6:
            {
                "tcp_in":[j.tcp_ports_in() for j in i.port_lists.all()],
                "tcp_out":[j.tcp_ports_out()for j in i.port_lists.all()],
                "udp_in":[j.udp_ports_in() for j in i.port_lists.all()],
                "udp_out":[j.udp_ports_out() for j in i.port_lists.all()],
            }
                for i in Interface.objects.all() if i.ipv6
        }
