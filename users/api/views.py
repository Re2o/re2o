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

import users.models as users

from preferences.models import OptionalUser

from . import serializers
from api.pagination import PageSizedPagination
from api.permissions import ACLPermission

# USER


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Users` objects.
    """
    queryset = users.User.objects.all()
    serializer_class = serializers.UserSerializer


class HomeCreationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users` objects to create homes.
    """
    queryset = users.User.objects.exclude(Q(state=users.User.STATE_DISABLED) | Q(state=users.User.STATE_NOT_YET_ACTIVE))
    serializer_class = serializers.BasicUserSerializer


class NormalUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users`without specific rights objects."""
    queryset = users.User.objects.exclude(groups__listright__critical=True).distinct()
    serializer_class = serializers.BasicUserSerializer


class CriticalUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users`without specific rights objects."""
    queryset = users.User.objects.filter(groups__listright__critical=True).distinct()
    serializer_class = serializers.BasicUserSerializer

class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Club` objects.
    """
    queryset = users.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class AdherentViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Adherent` objects.
    """
    queryset = users.Adherent.objects.all()
    serializer_class = serializers.AdherentSerializer


class ServiceUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ServiceUser` objects.
    """
    queryset = users.ServiceUser.objects.all()
    serializer_class = serializers.ServiceUserSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.School` objects.
    """
    queryset = users.School.objects.all()
    serializer_class = serializers.SchoolSerializer


class ListRightViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListRight` objects.
    """
    queryset = users.ListRight.objects.all()
    serializer_class = serializers.ListRightSerializer


class ShellViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListShell` objects.
    """
    queryset = users.ListShell.objects.all()
    serializer_class = serializers.ShellSerializer


class BanViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Ban` objects.
    """
    queryset = users.Ban.objects.all()
    serializer_class = serializers.BanSerializer


class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Whitelist` objects.
    """
    queryset = users.Whitelist.objects.all()
    serializer_class = serializers.WhitelistSerializer


class EMailAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.EMailAddress` objects.
    """
    serializer_class = serializers.EMailAddressSerializer
    queryset = users.EMailAddress.objects.none()

    def get_queryset(self):
        if OptionalUser.get_cached_value(
                'local_email_accounts_enabled'):
            return (users.EMailAddress.objects
                    .filter(user__local_email_enabled=True))
        else:
            return users.EMailAddress.objects.none()



