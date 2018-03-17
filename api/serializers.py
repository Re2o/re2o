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
from machines.models import Service_link


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
