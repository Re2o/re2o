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

"""Defines the views of the API

All views inherits the `rest_framework.views.APIview` to respect the
REST API requirements such as dealing with HTTP status code, format of
the response (JSON or other), the CSRF exempting, ...
"""

import datetime

from django.conf import settings
from django.db.models import Q
from rest_framework import viewsets, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

import topologie.models as topologie

from . import serializers
from api.pagination import PageSizedPagination
from api.permissions import ACLPermission

class StackViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Stack` objects.
    """
    queryset = topologie.Stack.objects.all()
    serializer_class = serializers.StackSerializer


class AccessPointViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.AccessPoint` objects.
    """
    queryset = topologie.AccessPoint.objects.all()
    serializer_class = serializers.AccessPointSerializer


class SwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Switch` objects.
    """
    queryset = topologie.Switch.objects.all()
    serializer_class = serializers.SwitchSerializer


class ServerViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Server` objects.
    """
    queryset = topologie.Server.objects.all()
    serializer_class = serializers.ServerSerializer


class ModelSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.ModelSwitch` objects.
    """
    queryset = topologie.ModelSwitch.objects.all()
    serializer_class = serializers.ModelSwitchSerializer


class ConstructorSwitchViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.ConstructorSwitch`
    objects.
    """
    queryset = topologie.ConstructorSwitch.objects.all()
    serializer_class = serializers.ConstructorSwitchSerializer


class SwitchBayViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.SwitchBay` objects.
    """
    queryset = topologie.SwitchBay.objects.all()
    serializer_class = serializers.SwitchBaySerializer


class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Building` objects.
    """
    queryset = topologie.Building.objects.all()
    serializer_class = serializers.BuildingSerializer


class SwitchPortViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Port` objects.
    """
    queryset = topologie.Port.objects.all()
    serializer_class = serializers.SwitchPortSerializer


class PortProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.PortProfile` objects.
    """
    queryset = topologie.PortProfile.objects.all()
    serializer_class = serializers.PortProfileSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.Room` objects.
    """
    queryset = topologie.Room.objects.all()
    serializer_class = serializers.RoomSerializer


class PortProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `topologie.models.PortProfile` objects.
    """
    queryset = topologie.PortProfile.objects.all()
    serializer_class = serializers.PortProfileSerializer
