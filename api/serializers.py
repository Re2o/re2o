# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Mael Kervella
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

"""
Serializers for the API app
"""

from rest_framework import serializers
from users.models import Club, Adherent
from machines.models import (
    Interface,
    Service_link,
)


class ServiceLinkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='service.service_type')

    class Meta:
        model = Service_link
        fields = ('name',)


class MailingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='pseudo')

    class Meta:
        model = Club
        fields = ('name',)


class MailingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adherent
        fields = ('email', 'name', 'surname', 'pseudo',)


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


class ServicesSerializer(serializers.ModelSerializer):
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
