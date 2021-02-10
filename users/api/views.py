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

from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import generics, views, viewsets

import preferences.models as preferences
import users.models as users
from api.pagination import PageSizedPagination
from api.permissions import ACLPermission
from re2o.utils import all_has_access

from . import serializers


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Users` objects."""

    queryset = users.User.objects.all()
    serializer_class = serializers.UserSerializer


class HomeCreationViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes infos of `users.models.Users` objects to create homes."""

    queryset = users.User.objects.exclude(
        Q(state=users.User.STATE_DISABLED)
        | Q(state=users.User.STATE_NOT_YET_ACTIVE)
        | Q(state=users.User.STATE_FULL_ARCHIVE)
    )
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
    """Exposes list and details of `users.models.Club` objects."""

    queryset = users.Club.objects.all()
    serializer_class = serializers.ClubSerializer


class AdherentViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Adherent` objects."""

    queryset = users.Adherent.objects.all()
    serializer_class = serializers.AdherentSerializer


class ServiceUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ServiceUser` objects."""

    queryset = users.ServiceUser.objects.all()
    serializer_class = serializers.ServiceUserSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.School` objects."""

    queryset = users.School.objects.all()
    serializer_class = serializers.SchoolSerializer


class ListRightViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListRight` objects."""

    queryset = users.ListRight.objects.all()
    serializer_class = serializers.ListRightSerializer


class ShellViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.ListShell` objects."""

    queryset = users.ListShell.objects.all()
    serializer_class = serializers.ShellSerializer


class BanViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Ban` objects."""

    queryset = users.Ban.objects.all()
    serializer_class = serializers.BanSerializer


class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.Whitelist` objects."""

    queryset = users.Whitelist.objects.all()
    serializer_class = serializers.WhitelistSerializer


class EMailAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """Exposes list and details of `users.models.EMailAddress` objects."""

    serializer_class = serializers.EMailAddressSerializer
    queryset = users.EMailAddress.objects.none()

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return users.EMailAddress.objects.filter(user__local_email_enabled=True)
        else:
            return users.EMailAddress.objects.none()


class LocalEmailUsersView(generics.ListAPIView):
    """Exposes all the aliases of the users that activated the internal address"""

    serializer_class = serializers.LocalEmailUsersSerializer

    def get_queryset(self):
        if preferences.OptionalUser.get_cached_value("local_email_accounts_enabled"):
            return users.User.objects.filter(local_email_enabled=True)
        else:
            return users.User.objects.none()


class StandardMailingView(views.APIView):
    """Exposes list and details of standard mailings (name and members) in
    order to building the corresponding mailing lists.
    """

    pagination_class = PageSizedPagination
    permission_classes = (ACLPermission,)
    perms_map = {"GET": [users.User.can_view_all]}

    def get(self, request, format=None):
        adherents_data = serializers.MailingMemberSerializer(
            all_has_access(), many=True
        ).data

        data = [{"name": "adherents", "members": adherents_data}]
        groups = Group.objects.all()
        for group in groups:
            group_data = serializers.MailingMemberSerializer(
                group.user_set.all(), many=True
            ).data
            data.append({"name": group.name, "members": group_data})

        paginator = self.pagination_class()
        paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(data)


class ClubMailingView(generics.ListAPIView):
    """Exposes list and details of club mailings (name, members and admins) in
    order to build the corresponding mailing lists.
    """

    queryset = users.Club.objects.all()
    serializer_class = serializers.MailingSerializer
