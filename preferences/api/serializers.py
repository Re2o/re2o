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

import preferences.models as preferences
from api.serializers import NamespacedHRField, NamespacedHIField, NamespacedHMSerializer

class OptionalUserSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.OptionalUser` objects.
    """

    tel_mandatory = serializers.BooleanField(source="is_tel_mandatory")
    shell_default = serializers.StringRelatedField()

    class Meta:
        model = preferences.OptionalUser
        fields = (
            "tel_mandatory",
            "gpg_fingerprint",
            "all_can_create_club",
            "self_adhesion",
            "shell_default",
            "self_change_shell",
            "local_email_accounts_enabled",
            "local_email_domain",
            "max_email_address",
        )


class OptionalMachineSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.OptionalMachine` objects.
    """

    class Meta:
        model = preferences.OptionalMachine
        fields = (
            "password_machine",
            "max_lambdauser_interfaces",
            "max_lambdauser_aliases",
            "ipv6_mode",
            "create_machine",
            "ipv6",
            "default_dns_ttl"
        )


class OptionalTopologieSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.OptionalTopologie` objects.
    """

    switchs_management_interface_ip = serializers.CharField()

    class Meta:
        model = preferences.OptionalTopologie
        fields = (
            "switchs_ip_type",
            "switchs_web_management",
            "switchs_web_management_ssl",
            "switchs_rest_management",
            "switchs_management_utils",
            "switchs_management_interface_ip",
            "provision_switchs_enabled",
            "switchs_provision",
            "switchs_management_sftp_creds",
        )


class RadiusOptionSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.RadiusOption` objects
    """

    class Meta:
        model = preferences.RadiusOption
        fields = (
            "radius_general_policy",
            "unknown_machine",
            "unknown_machine_vlan",
            "unknown_port",
            "unknown_port_vlan",
            "unknown_room",
            "unknown_room_vlan",
            "non_member",
            "non_member_vlan",
            "banned",
            "banned_vlan",
            "vlan_decision_ok",
        )


class GeneralOptionSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.GeneralOption` objects.
    """

    class Meta:
        model = preferences.GeneralOption
        fields = (
            "general_message_fr",
            "general_message_en",
            "search_display_page",
            "pagination_number",
            "pagination_large_number",
            "req_expire_hrs",
            "site_name",
            "main_site_url",
            "email_from",
            "GTU_sum_up",
            "GTU",
        )


class HomeServiceSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.Service` objects.
    """

    class Meta:
        model = preferences.Service
        fields = ("name", "url", "description", "image", "api_url")
        extra_kwargs = {"api_url": {"view_name": "homeservice-detail"}}


class AssoOptionSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.AssoOption` objects.
    """

    class Meta:
        model = preferences.AssoOption
        fields = (
            "name",
            "siret",
            "adresse1",
            "adresse2",
            "contact",
            "telephone",
            "pseudo",
            "utilisateur_asso",
            "description",
        )


class HomeOptionSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.HomeOption` objects.
    """

    class Meta:
        model = preferences.HomeOption
        fields = ("facebook_url", "twitter_url", "twitter_account_name")


class MailMessageOptionSerializer(NamespacedHMSerializer):
    """Serialize `preferences.models.MailMessageOption` objects.
    """

    class Meta:
        model = preferences.MailMessageOption
        fields = ("welcome_mail_fr", "welcome_mail_en")
