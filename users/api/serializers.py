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

from rest_framework import serializers

import users.models as users
from api.serializers import (NamespacedHIField, NamespacedHMSerializer,
                             NamespacedHRField)


class UserSerializer(NamespacedHMSerializer):
    """Serialize `users.models.User` objects."""

    access = serializers.BooleanField(source="has_access")
    uid = serializers.IntegerField(source="uid_number")

    class Meta:
        model = users.User
        fields = (
            "surname",
            "pseudo",
            "email",
            "local_email_redirect",
            "local_email_enabled",
            "school",
            "shell",
            "comment",
            "state",
            "registered",
            "telephone",
            "solde",
            "access",
            "end_access",
            "uid",
            "class_type",
            "api_url",
        )
        extra_kwargs = {"shell": {"view_name": "shell-detail"}}


class ClubSerializer(NamespacedHMSerializer):
    """Serialize `users.models.Club` objects."""

    name = serializers.CharField(source="surname")
    access = serializers.BooleanField(source="has_access")
    uid = serializers.IntegerField(source="uid_number")

    class Meta:
        model = users.Club
        fields = (
            "name",
            "pseudo",
            "email",
            "local_email_redirect",
            "local_email_enabled",
            "school",
            "shell",
            "comment",
            "state",
            "registered",
            "telephone",
            "solde",
            "room",
            "access",
            "end_access",
            "administrators",
            "members",
            "mailing",
            "uid",
            "api_url",
        )
        extra_kwargs = {"shell": {"view_name": "shell-detail"}}


class AdherentSerializer(NamespacedHMSerializer):
    """Serialize `users.models.Adherent` objects."""

    access = serializers.BooleanField(source="has_access")
    uid = serializers.IntegerField(source="uid_number")

    class Meta:
        model = users.Adherent
        fields = (
            "name",
            "surname",
            "pseudo",
            "email",
            "local_email_redirect",
            "local_email_enabled",
            "school",
            "shell",
            "comment",
            "state",
            "registered",
            "telephone",
            "room",
            "solde",
            "access",
            "end_access",
            "uid",
            "api_url",
            "gid",
        )
        extra_kwargs = {"shell": {"view_name": "shell-detail"}}


class BasicUserSerializer(NamespacedHMSerializer):
    """Serialize 'users.models.User' minimal infos"""

    uid = serializers.IntegerField(source="uid_number")
    gid = serializers.IntegerField(source="gid_number")

    class Meta:
        model = users.User
        fields = ("pseudo", "uid", "gid")


class ServiceUserSerializer(NamespacedHMSerializer):
    """Serialize `users.models.ServiceUser` objects."""

    class Meta:
        model = users.ServiceUser
        fields = ("pseudo", "access_group", "comment", "api_url")


class SchoolSerializer(NamespacedHMSerializer):
    """Serialize `users.models.School` objects."""

    class Meta:
        model = users.School
        fields = ("name", "api_url")


class ListRightSerializer(NamespacedHMSerializer):
    """Serialize `users.models.ListRight` objects."""

    class Meta:
        model = users.ListRight
        fields = ("unix_name", "gid", "critical", "details", "api_url")


class ShellSerializer(NamespacedHMSerializer):
    """Serialize `users.models.ListShell` objects."""

    class Meta:
        model = users.ListShell
        fields = ("shell", "api_url")
        extra_kwargs = {"api_url": {"view_name": "shell-detail"}}


class BanSerializer(NamespacedHMSerializer):
    """Serialize `users.models.Ban` objects."""

    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = users.Ban
        fields = (
            "user",
            "raison",
            "date_start",
            "date_end",
            "state",
            "active",
            "api_url",
        )


class WhitelistSerializer(NamespacedHMSerializer):
    """Serialize `users.models.Whitelist` objects."""

    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = users.Whitelist
        fields = ("user", "raison", "date_start", "date_end", "active", "api_url")


class EMailAddressSerializer(NamespacedHMSerializer):
    """Serialize `users.models.EMailAddress` objects."""

    user = serializers.CharField(source="user.pseudo", read_only=True)

    class Meta:
        model = users.EMailAddress
        fields = ("user", "local_part", "complete_email_address", "api_url")


class LocalEmailUsersSerializer(NamespacedHMSerializer):
    email_address = EMailAddressSerializer(read_only=True, many=True)

    class Meta:
        model = users.User
        fields = (
            "local_email_enabled",
            "local_email_redirect",
            "email_address",
            "email",
        )


class MailingMemberSerializer(UserSerializer):
    """Serialize the data about a mailing member."""

    class Meta(UserSerializer.Meta):
        fields = ("name", "pseudo", "get_mail")


class MailingSerializer(ClubSerializer):
    """Serialize the data about a mailing."""

    members = MailingMemberSerializer(many=True)
    admins = MailingMemberSerializer(source="administrators", many=True)

    class Meta(ClubSerializer.Meta):
        fields = ("name", "members", "admins")
