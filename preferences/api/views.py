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

from rest_framework import viewsets, generics

from . import serializers
import preferences.models as preferences
from api.permissions import ACLPermission


class OptionalUserView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalUser.can_view_all]}
    serializer_class = serializers.OptionalUserSerializer

    def get_object(self):
        return preferences.OptionalUser.objects.first()


class OptionalMachineView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalMachine` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalMachine.can_view_all]}
    serializer_class = serializers.OptionalMachineSerializer

    def get_object(self):
        return preferences.OptionalMachine.objects.first()


class OptionalTopologieView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalTopologie` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.OptionalTopologie.can_view_all]}
    serializer_class = serializers.OptionalTopologieSerializer

    def get_object(self):
        return preferences.OptionalTopologie.objects.first()


class RadiusOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.OptionalTopologie` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.RadiusOption.can_view_all]}
    serializer_class = serializers.RadiusOptionSerializer

    def get_object(self):
        return preferences.RadiusOption.objects.first()


class GeneralOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.GeneralOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.GeneralOption.can_view_all]}
    serializer_class = serializers.GeneralOptionSerializer

    def get_object(self):
        return preferences.GeneralOption.objects.first()


class HomeServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `preferences.models.Service` objects.
    """

    queryset = preferences.Service.objects.all()
    serializer_class = serializers.HomeServiceSerializer


class AssoOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.AssoOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.AssoOption.can_view_all]}
    serializer_class = serializers.AssoOptionSerializer

    def get_object(self):
        return preferences.AssoOption.objects.first()


class HomeOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.HomeOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.HomeOption.can_view_all]}
    serializer_class = serializers.HomeOptionSerializer

    def get_object(self):
        return preferences.HomeOption.objects.first()


class MailMessageOptionView(generics.RetrieveAPIView):
    """Exposes details of `preferences.models.MailMessageOption` settings.
    """

    permission_classes = (ACLPermission,)
    perms_map = {"GET": [preferences.MailMessageOption.can_view_all]}
    serializer_class = serializers.MailMessageOptionSerializer

    def get_object(self):
        return preferences.MailMessageOption.objects.first()