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

"""Defines the serializers of the API
"""

from rest_framework import serializers

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users

# The namespace used for the API. It must match the namespace used in the
# urlpatterns to include the API URLs.
API_NAMESPACE = "api"


class NamespacedHRField(serializers.HyperlinkedRelatedField):
    """A `rest_framework.serializers.HyperlinkedRelatedField` subclass to
    automatically prefix view names with the API namespace.
    """

    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = "%s:%s" % (API_NAMESPACE, view_name)
        super(NamespacedHRField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHIField(serializers.HyperlinkedIdentityField):
    """A `rest_framework.serializers.HyperlinkedIdentityField` subclass to
    automatically prefix view names with teh API namespace.
    """

    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = "%s:%s" % (API_NAMESPACE, view_name)
        super(NamespacedHIField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHMSerializer(serializers.HyperlinkedModelSerializer):
    """A `rest_framework.serializers.HyperlinkedModelSerializer` subclass to
    automatically prefix view names with the API namespace.
    """

    serializer_related_field = NamespacedHRField
    serializer_url_field = NamespacedHIField


# COTISATIONS


class FactureSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Facture` objects.
    """

    class Meta:
        model = cotisations.Facture
        fields = (
            "user",
            "paiement",
            "banque",
            "cheque",
            "date",
            "valid",
            "control",
            "prix_total",
            "name",
            "api_url",
        )


class BaseInvoiceSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.BaseInvoice
        fields = "__all__"


class VenteSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Vente` objects.
    """

    class Meta:
        model = cotisations.Vente
        fields = (
            "facture",
            "number",
            "name",
            "prix",
            "duration",
            "type_cotisation",
            "prix_total",
            "api_url",
        )


class ArticleSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Article` objects.
    """

    class Meta:
        model = cotisations.Article
        fields = ("name", "prix", "duration", "type_user", "type_cotisation", "api_url")


class BanqueSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Banque` objects.
    """

    class Meta:
        model = cotisations.Banque
        fields = ("name", "api_url")


class PaiementSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Paiement` objects.
    """

    class Meta:
        model = cotisations.Paiement
        fields = ("moyen", "api_url")


class CotisationSerializer(NamespacedHMSerializer):
    """Serialize `cotisations.models.Cotisation` objects.
    """

    class Meta:
        model = cotisations.Cotisation
        fields = ("vente", "type_cotisation", "date_start", "date_end", "api_url")


# MACHINES


class MachineSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Machine` objects.
    """

    class Meta:
        model = machines.Machine
        fields = ("user", "name", "active", "api_url")


class MachineTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.MachineType` objects.
    """

    class Meta:
        model = machines.MachineType
        fields = ("name", "ip_type", "api_url")


class IpTypeSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpType` objects.
    """

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "extension",
            "need_infra",
            "domaine_ip_start",
            "domaine_ip_stop",
            "prefix_v6",
            "vlan",
            "ouverture_ports",
            "api_url",
        )


class VlanSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Vlan` objects.
    """

    class Meta:
        model = machines.Vlan
        fields = (
            "vlan_id",
            "name",
            "comment",
            "arp_protect",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "igmp",
            "mld",
            "api_url",
        )


class NasSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Nas` objects.
    """

    class Meta:
        model = machines.Nas
        fields = (
            "name",
            "nas_type",
            "machine_type",
            "port_access_mode",
            "autocapture_mac",
            "api_url",
        )


class SOASerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SOA` objects.
    """

    class Meta:
        model = machines.SOA
        fields = ("name", "mail", "refresh", "retry", "expire", "ttl", "api_url")


class ExtensionSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Extension` objects.
    """

    class Meta:
        model = machines.Extension
        fields = ("name", "need_infra", "origin", "origin_v6", "soa", "api_url")


class MxSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Mx` objects.
    """

    class Meta:
        model = machines.Mx
        fields = ("zone", "priority", "name", "api_url")


class DNameSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.DName` objects.
    """

    class Meta:
        model = machines.DName
        fields = ("zone", "alias", "api_url")


class NsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ns` objects.
    """

    class Meta:
        model = machines.Ns
        fields = ("zone", "ns", "api_url")


class TxtSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Txt` objects.
    """

    class Meta:
        model = machines.Txt
        fields = ("zone", "field1", "field2", "api_url")


class SrvSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Srv` objects.
    """

    class Meta:
        model = machines.Srv
        fields = (
            "service",
            "protocole",
            "extension",
            "ttl",
            "priority",
            "weight",
            "port",
            "target",
            "api_url",
        )


class SshFpSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.SSHFP` objects.
    """

    class Meta:
        model = machines.SshFp
        field = ("machine", "pub_key_entry", "algo", "comment", "api_url")


class InterfaceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Interface` objects.
    """

    mac_address = serializers.CharField()
    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = machines.Interface
        fields = (
            "ipv4",
            "mac_address",
            "machine",
            "machine_type",
            "details",
            "port_lists",
            "active",
            "api_url",
        )


class Ipv6ListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """

    class Meta:
        model = machines.Ipv6List
        fields = ("ipv6", "interface", "slaac_ip", "api_url")


class DomainSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Domain` objects.
    """

    class Meta:
        model = machines.Domain
        fields = ("interface_parent", "name", "extension", "cname", "api_url")


class IpListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.IpList` objects.
    """

    class Meta:
        model = machines.IpList
        fields = ("ipv4", "ip_type", "need_infra", "api_url")


class ServiceSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service` objects.
    """

    class Meta:
        model = machines.Service
        fields = (
            "service_type",
            "min_time_regen",
            "regular_time_regen",
            "servers",
            "api_url",
        )


class ServiceLinkSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Service_link` objects.
    """

    class Meta:
        model = machines.Service_link
        fields = (
            "service",
            "server",
            "last_regen",
            "asked_regen",
            "need_regen",
            "api_url",
        )
        extra_kwargs = {"api_url": {"view_name": "servicelink-detail"}}


class OuverturePortListSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePortList` objects.
    """

    tcp_ports_in = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    udp_ports_in = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    tcp_ports_out = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )
    udp_ports_out = NamespacedHRField(
        view_name="ouvertureport-detail", many=True, read_only=True
    )

    class Meta:
        model = machines.OuverturePortList
        fields = (
            "name",
            "tcp_ports_in",
            "udp_ports_in",
            "tcp_ports_out",
            "udp_ports_out",
            "api_url",
        )


class OuverturePortSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    class Meta:
        model = machines.OuverturePort
        fields = ("begin", "end", "port_list", "protocole", "io", "api_url")


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    servers = InterfaceSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ("role_type", "servers", "api_url")


# PREFERENCES


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


# TOPOLOGIE


class StackSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Stack` objects
    """

    class Meta:
        model = topologie.Stack
        fields = (
            "name",
            "stack_id",
            "details",
            "member_id_min",
            "member_id_max",
            "api_url",
        )


class AccessPointSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.AccessPoint` objects
    """

    class Meta:
        model = topologie.AccessPoint
        fields = ("user", "name", "active", "location", "api_url")


class SwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Switch` objects
    """

    port_amount = serializers.IntegerField(source="number")

    class Meta:
        model = topologie.Switch
        fields = (
            "user",
            "name",
            "active",
            "port_amount",
            "stack",
            "stack_member_id",
            "model",
            "switchbay",
            "api_url",
        )


class ServerSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Server` objects
    """

    class Meta:
        model = topologie.Server
        fields = ("user", "name", "active", "api_url")


class ModelSwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.ModelSwitch` objects
    """

    class Meta:
        model = topologie.ModelSwitch
        fields = ("reference", "constructor", "api_url")


class ConstructorSwitchSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.ConstructorSwitch` objects
    """

    class Meta:
        model = topologie.ConstructorSwitch
        fields = ("name", "api_url")


class SwitchBaySerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.SwitchBay` objects
    """

    class Meta:
        model = topologie.SwitchBay
        fields = ("name", "building", "info", "api_url")


class BuildingSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Building` objects
    """

    class Meta:
        model = topologie.Building
        fields = ("name", "api_url")


class SwitchPortSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Port` objects
    """

    get_port_profile = NamespacedHIField(view_name="portprofile-detail", read_only=True)

    class Meta:
        model = topologie.Port
        fields = (
            "switch",
            "port",
            "room",
            "machine_interface",
            "related",
            "custom_profile",
            "state",
            "get_port_profile",
            "details",
            "api_url",
        )
        extra_kwargs = {
            "related": {"view_name": "switchport-detail"},
            "api_url": {"view_name": "switchport-detail"},
        }


class PortProfileSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Room` objects
    """

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "api_url",
        )


class RoomSerializer(NamespacedHMSerializer):
    """Serialize `topologie.models.Room` objects
    """

    class Meta:
        model = topologie.Room
        fields = ("name", "details", "api_url")


class PortProfileSerializer(NamespacedHMSerializer):
    vlan_untagged = VlanSerializer(read_only=True)

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "vlan_untagged",
            "vlan_tagged",
        )


# USERS


class UserSerializer(NamespacedHMSerializer):
    """Serialize `users.models.User` objects.
    """

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
    """Serialize `users.models.Club` objects.
    """

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
    """Serialize `users.models.Adherent` objects.
    """

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
    """Serialize `users.models.ServiceUser` objects.
    """

    class Meta:
        model = users.ServiceUser
        fields = ("pseudo", "access_group", "comment", "api_url")


class SchoolSerializer(NamespacedHMSerializer):
    """Serialize `users.models.School` objects.
    """

    class Meta:
        model = users.School
        fields = ("name", "api_url")


class ListRightSerializer(NamespacedHMSerializer):
    """Serialize `users.models.ListRight` objects.
    """

    class Meta:
        model = users.ListRight
        fields = ("unix_name", "gid", "critical", "details", "api_url")


class ShellSerializer(NamespacedHMSerializer):
    """Serialize `users.models.ListShell` objects.
    """

    class Meta:
        model = users.ListShell
        fields = ("shell", "api_url")
        extra_kwargs = {"api_url": {"view_name": "shell-detail"}}


class BanSerializer(NamespacedHMSerializer):
    """Serialize `users.models.Ban` objects.
    """

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
    """Serialize `users.models.Whitelist` objects.
    """

    active = serializers.BooleanField(source="is_active")

    class Meta:
        model = users.Whitelist
        fields = ("user", "raison", "date_start", "date_end", "active", "api_url")


class EMailAddressSerializer(NamespacedHMSerializer):
    """Serialize `users.models.EMailAddress` objects.
    """

    user = serializers.CharField(source="user.pseudo", read_only=True)

    class Meta:
        model = users.EMailAddress
        fields = ("user", "local_part", "complete_email_address", "api_url")


# SERVICE REGEN


class ServiceRegenSerializer(NamespacedHMSerializer):
    """Serialize the data about the services to regen.
    """

    hostname = serializers.CharField(source="server.domain.name", read_only=True)
    service_name = serializers.CharField(source="service.service_type", read_only=True)
    need_regen = serializers.BooleanField()

    class Meta:
        model = machines.Service_link
        fields = ("hostname", "service_name", "need_regen", "api_url")
        extra_kwargs = {"api_url": {"view_name": "serviceregen-detail"}}


# Switches et ports


class InterfaceVlanSerializer(NamespacedHMSerializer):
    domain = serializers.CharField(read_only=True)
    ipv4 = serializers.CharField(read_only=True)
    ipv6 = Ipv6ListSerializer(read_only=True, many=True)
    vlan_id = serializers.IntegerField(
        source="machine_type.ip_type.vlan.vlan_id", read_only=True
    )

    class Meta:
        model = machines.Interface
        fields = ("ipv4", "ipv6", "domain", "vlan_id")


class InterfaceRoleSerializer(NamespacedHMSerializer):
    interface = InterfaceVlanSerializer(
        source="machine.interface_set", read_only=True, many=True
    )

    class Meta:
        model = machines.Interface
        fields = ("interface",)


class RoleSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.OuverturePort` objects.
    """

    servers = InterfaceRoleSerializer(read_only=True, many=True)

    class Meta:
        model = machines.Role
        fields = ("role_type", "servers", "specific_role")


class VlanPortSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Vlan
        fields = ("vlan_id", "name")


class ProfilSerializer(NamespacedHMSerializer):
    vlan_untagged = VlanSerializer(read_only=True)
    vlan_tagged = VlanPortSerializer(read_only=True, many=True)

    class Meta:
        model = topologie.PortProfile
        fields = (
            "name",
            "profil_default",
            "vlan_untagged",
            "vlan_tagged",
            "radius_type",
            "radius_mode",
            "speed",
            "mac_limit",
            "flow_control",
            "dhcp_snooping",
            "dhcpv6_snooping",
            "arp_protect",
            "ra_guard",
            "loop_protect",
            "vlan_untagged",
            "vlan_tagged",
        )


class ModelSwitchSerializer(NamespacedHMSerializer):
    constructor = serializers.CharField(read_only=True)

    class Meta:
        model = topologie.ModelSwitch
        fields = ("reference", "firmware", "constructor")


class SwitchBaySerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.SwitchBay
        fields = ("name",)


class PortsSerializer(NamespacedHMSerializer):
    """Serialize `machines.models.Ipv6List` objects.
    """

    get_port_profile = ProfilSerializer(read_only=True)

    class Meta:
        model = topologie.Port
        fields = ("state", "port", "pretty_name", "get_port_profile")


class SwitchPortSerializer(serializers.ModelSerializer):
    """Serialize the data about the switches"""

    ports = PortsSerializer(many=True, read_only=True)
    model = ModelSwitchSerializer(read_only=True)
    switchbay = SwitchBaySerializer(read_only=True)

    class Meta:
        model = topologie.Switch
        fields = (
            "short_name",
            "model",
            "switchbay",
            "ports",
            "ipv4",
            "ipv6",
            "interfaces_subnet",
            "interfaces6_subnet",
            "automatic_provision",
            "rest_enabled",
            "web_management_enabled",
            "get_radius_key_value",
            "get_management_cred_value",
            "get_radius_servers",
            "list_modules",
        )


# LOCAL EMAILS


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


# Firewall


class FirewallPortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = machines.OuverturePort
        fields = ("begin", "end", "protocole", "io", "show_port")


class FirewallOuverturePortListSerializer(serializers.ModelSerializer):
    tcp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_in = FirewallPortListSerializer(many=True, read_only=True)
    tcp_ports_out = FirewallPortListSerializer(many=True, read_only=True)
    udp_ports_out = FirewallPortListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.OuverturePortList
        fields = ("tcp_ports_in", "udp_ports_in", "tcp_ports_out", "udp_ports_out")


class SubnetPortsOpenSerializer(serializers.ModelSerializer):
    ouverture_ports = FirewallOuverturePortListSerializer(read_only=True)

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "domaine_ip_start",
            "domaine_ip_stop",
            "complete_prefixv6",
            "ouverture_ports",
        )


class InterfacePortsOpenSerializer(serializers.ModelSerializer):
    port_lists = FirewallOuverturePortListSerializer(read_only=True, many=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("port_lists", "ipv4", "ipv6")


# DHCP


class HostMacIpSerializer(serializers.ModelSerializer):
    """Serialize the data about the hostname-ipv4-mac address association
    to build the DHCP lease files.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    extension = serializers.CharField(source="domain.extension.name", read_only=True)
    mac_address = serializers.CharField(read_only=True)
    ip_type = serializers.CharField(source="machine_type.ip_type", read_only=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "extension", "mac_address", "ipv4", "ip_type")


# DNS


class SOARecordSerializer(SOASerializer):
    """Serialize `machines.models.SOA` objects with the data needed to
    generate a SOA DNS record.
    """

    class Meta:
        model = machines.SOA
        fields = ("name", "mail", "refresh", "retry", "expire", "ttl")


class OriginV4RecordSerializer(IpListSerializer):
    """Serialize `machines.models.IpList` objects with the data needed to
    generate an IPv4 Origin DNS record.
    """

    class Meta(IpListSerializer.Meta):
        fields = ("ipv4",)


class NSRecordSerializer(NsSerializer):
    """Serialize `machines.models.Ns` objects with the data needed to
    generate a NS DNS record.
    """

    target = serializers.CharField(source="ns", read_only=True)

    class Meta(NsSerializer.Meta):
        fields = ("target",)


class MXRecordSerializer(MxSerializer):
    """Serialize `machines.models.Mx` objects with the data needed to
    generate a MX DNS record.
    """

    target = serializers.CharField(source="name", read_only=True)

    class Meta(MxSerializer.Meta):
        fields = ("target", "priority")


class TXTRecordSerializer(TxtSerializer):
    """Serialize `machines.models.Txt` objects with the data needed to
    generate a TXT DNS record.
    """

    class Meta(TxtSerializer.Meta):
        fields = ("field1", "field2")


class SRVRecordSerializer(SrvSerializer):
    """Serialize `machines.models.Srv` objects with the data needed to
    generate a SRV DNS record.
    """

    target = serializers.CharField(source="target.name", read_only=True)

    class Meta(SrvSerializer.Meta):
        fields = ("service", "protocole", "ttl", "priority", "weight", "port", "target")


class SSHFPRecordSerializer(SshFpSerializer):
    """Serialize `machines.models.SshFp` objects with the data needed to
    generate a SSHFP DNS record.
    """

    class Meta(SshFpSerializer.Meta):
        fields = ("algo_id", "hash")


class SSHFPInterfaceSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    sshfp = SSHFPRecordSerializer(source="machine.sshfp_set", many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "sshfp")


class ARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a A DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    ipv4 = serializers.CharField(source="ipv4.ipv4", read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "ipv4")


class AAAARecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Interface` objects with the data needed to
    generate a AAAA DNS record.
    """

    hostname = serializers.CharField(source="domain.name", read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ("hostname", "ipv6")


class CNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a CNAME DNS record.
    """

    alias = serializers.CharField(source="cname", read_only=True)
    hostname = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = machines.Domain
        fields = ("alias", "hostname")


class DNAMERecordSerializer(serializers.ModelSerializer):
    """Serialize `machines.models.Domain` objects with the data needed to
    generate a DNAME DNS record.
    """

    alias = serializers.CharField(read_only=True)
    zone = serializers.CharField(read_only=True)

    class Meta:
        model = machines.DName
        fields = ("alias", "zone")


class DNSZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """

    soa = SOARecordSerializer()
    ns_records = NSRecordSerializer(many=True, source="ns_set")
    originv4 = OriginV4RecordSerializer(source="origin")
    originv6 = serializers.CharField(source="origin_v6")
    mx_records = MXRecordSerializer(many=True, source="mx_set")
    txt_records = TXTRecordSerializer(many=True, source="txt_set")
    srv_records = SRVRecordSerializer(many=True, source="srv_set")
    a_records = ARecordSerializer(many=True, source="get_associated_a_records")
    aaaa_records = AAAARecordSerializer(many=True, source="get_associated_aaaa_records")
    cname_records = CNAMERecordSerializer(
        many=True, source="get_associated_cname_records"
    )
    dname_records = DNAMERecordSerializer(
        many=True, source="get_associated_dname_records"
    )
    sshfp_records = SSHFPInterfaceSerializer(
        many=True, source="get_associated_sshfp_records"
    )

    class Meta:
        model = machines.Extension
        fields = (
            "name",
            "soa",
            "ns_records",
            "originv4",
            "originv6",
            "mx_records",
            "txt_records",
            "srv_records",
            "a_records",
            "aaaa_records",
            "cname_records",
            "dname_records",
            "sshfp_records",
        )


# REMINDER


class ReminderUsersSerializer(UserSerializer):
    """Serialize the data about a mailing member.
    """

    class Meta(UserSerializer.Meta):
        fields = ("get_full_name", "get_mail")


class ReminderSerializer(serializers.ModelSerializer):
    """
    Serialize the data about a reminder
    """

    users_to_remind = ReminderUsersSerializer(many=True)

    class Meta:
        model = preferences.Reminder
        fields = ("days", "message", "users_to_remind")


class DNSReverseZonesSerializer(serializers.ModelSerializer):
    """Serialize the data about DNS Zones.
    """

    soa = SOARecordSerializer(source="extension.soa")
    extension = serializers.CharField(source="extension.name", read_only=True)
    cidrs = serializers.ListField(
        child=serializers.CharField(), source="ip_set_cidrs_as_str", read_only=True
    )
    ns_records = NSRecordSerializer(many=True, source="extension.ns_set")
    mx_records = MXRecordSerializer(many=True, source="extension.mx_set")
    txt_records = TXTRecordSerializer(many=True, source="extension.txt_set")
    ptr_records = ARecordSerializer(many=True, source="get_associated_ptr_records")
    ptr_v6_records = AAAARecordSerializer(
        many=True, source="get_associated_ptr_v6_records"
    )

    class Meta:
        model = machines.IpType
        fields = (
            "name",
            "extension",
            "soa",
            "ns_records",
            "mx_records",
            "txt_records",
            "ptr_records",
            "ptr_v6_records",
            "cidrs",
            "prefix_v6",
            "prefix_v6_length",
        )


# MAILING


class MailingMemberSerializer(UserSerializer):
    """Serialize the data about a mailing member.
    """

    class Meta(UserSerializer.Meta):
        fields = ("name", "pseudo", "get_mail")


class MailingSerializer(ClubSerializer):
    """Serialize the data about a mailing.
    """

    members = MailingMemberSerializer(many=True)
    admins = MailingMemberSerializer(source="administrators", many=True)

    class Meta(ClubSerializer.Meta):
        fields = ("name", "members", "admins")
