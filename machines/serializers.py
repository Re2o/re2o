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
from machines.models import Interface, IpType, Extension, IpList, MachineType, Domain, Text, Mx, Service_link, Ns

class IpTypeField(serializers.RelatedField):
    def to_representation(self, value):
        return value.type

class IpListSerializer(serializers.ModelSerializer):
    ip_type = IpTypeField(read_only=True)

    class Meta:
        model = IpList
        fields = ('ipv4', 'ip_type')

class InterfaceSerializer(serializers.ModelSerializer):
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

class ExtensionNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

class TypeSerializer(serializers.ModelSerializer):
    extension = ExtensionNameField(read_only=True)

    class Meta:
        model = IpType
        fields = ('type', 'extension', 'domaine_ip_start', 'domaine_ip_stop')

class ExtensionSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField('get_origin_ip')

    class Meta:
        model = Extension
        fields = ('name', 'origin')

    def get_origin_ip(self, obj):
        return obj.origin.ipv4

class MxSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_mx_name')
    zone = serializers.SerializerMethodField('get_zone_name')

    class Meta:
        model = Mx
        fields = ('zone', 'priority', 'name')

    def get_mx_name(self, obj):
        return str(obj.name)

    def get_zone_name(self, obj):
        return obj.zone.name

class TextSerializer(serializers.ModelSerializer):
    zone = serializers.SerializerMethodField('get_zone_name')
    text = serializers.SerializerMethodField('get_text_name')

    class Meta:
        model = Text
        fields = ('zone','text')

    def get_zone_name(self, obj):
        return str(obj.zone.name)

    def get_text_name(self, obj):
        return str(obj.dns_entry)

class NsSerializer(serializers.ModelSerializer):
    zone = serializers.SerializerMethodField('get_zone_name')
    ns = serializers.SerializerMethodField('get_domain_name')

    class Meta:
        model = Ns
        fields = ('zone', 'ns')

    def get_zone_name(self, obj):
        return obj.zone.name

    def get_domain_name(self, obj):
        return str(obj.ns)

class DomainSerializer(serializers.ModelSerializer):
    extension = serializers.SerializerMethodField('get_zone_name')
    cname = serializers.SerializerMethodField('get_cname_name')

    class Meta:
        model = Domain
        fields = ('name', 'extension', 'cname')

    def get_zone_name(self, obj):
        return obj.extension.name

    def get_cname_name(self, obj):
        return str(obj.cname)

class ServiceServersSerializer(serializers.ModelSerializer):
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
