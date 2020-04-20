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
from django.contrib.auth.models import Group
from rest_framework import viewsets, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

# import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users
from re2o.utils import all_active_interfaces, all_has_access
from . import serializers
from .pagination import PageSizedPagination
from .permissions import ACLPermission



class ReminderView(generics.ListAPIView):
    """Output for users to remind an end of their subscription.
    """

    queryset = preferences.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer

class ObtainExpiringAuthToken(ObtainAuthToken):
    """Exposes a view to obtain a authentication token.

    This view as the same behavior as the
    `rest_framework.auth_token.views.ObtainAuthToken` view except that the
    expiration time is send along with the token as an addtional information.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        token_duration = datetime.timedelta(seconds=settings.API_TOKEN_DURATION)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if not created and token.created < utc_now - token_duration:
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow()
            token.save()

        return Response(
            {"token": token.key, "expiration": token.created + token_duration}
        )
