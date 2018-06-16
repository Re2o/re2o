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

import cotisations.models as cotisations
import machines.models as machines
import preferences.models as preferences
import topologie.models as topologie
import users.models as users


API_NAMESPACE = 'api'


class NamespacedHRField(serializers.HyperlinkedRelatedField):
    """ A HyperlinkedRelatedField subclass to automatically prefix
    view names with a namespace """
    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = '%s:%s' % (API_NAMESPACE, view_name)
        super(NamespacedHRField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHIField(serializers.HyperlinkedIdentityField):
    """ A HyperlinkedIdentityField subclass to automatically prefix
    view names with a namespace """
    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            view_name = '%s:%s' % (API_NAMESPACE, view_name)
        super(NamespacedHIField, self).__init__(view_name=view_name, **kwargs)


class NamespacedHMSerializer(serializers.HyperlinkedModelSerializer):
    """ A HyperlinkedModelSerializer subclass to use `NamespacedHRField` as
    field and automatically prefix view names with a namespace """
    serializer_related_field = NamespacedHRField
    serializer_url_field = NamespacedHIField


# COTISATIONS APP


class FactureSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Facture
        fields = ('user', 'paiement', 'banque', 'cheque', 'date', 'valid',
                  'control', 'prix_total', 'name', 'api_url')


class VenteSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Vente
        fields = ('facture', 'number', 'name', 'prix', 'duration',
                  'type_cotisation', 'prix_total', 'api_url')


class ArticleSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Article
        fields = ('name', 'prix', 'duration', 'type_user',
                  'type_cotisation', 'api_url')


class BanqueSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Banque
        fields = ('name', 'api_url')


class PaiementSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Paiement
        fields = ('moyen', 'type_paiement', 'api_url')


class CotisationSerializer(NamespacedHMSerializer):
    class Meta:
        model = cotisations.Cotisation
        fields = ('vente', 'type_cotisation', 'date_start', 'date_end',
                  'api_url')


# MACHINES APP


class MachineSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Machine
        fields = ('user', 'name', 'active', 'api_url')


class MachineTypeSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.MachineType
        fields = ('type', 'ip_type', 'api_url')


class IpTypeSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.IpType
        fields = ('type', 'extension', 'need_infra', 'domaine_ip_start',
                  'domaine_ip_stop', 'prefix_v6', 'vlan', 'ouverture_ports',
                  'api_url')


class VlanSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Vlan
        fields = ('vlan_id', 'name', 'comment', 'api_url')


class NasSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Nas
        fields = ('name', 'nas_type', 'machine_type', 'port_access_mode',
                  'autocapture_mac', 'api_url')


class SOASerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.SOA
        fields = ('name', 'mail', 'refresh', 'retry', 'expire', 'ttl',
                  'api_url')


class ExtensionSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Extension
        fields = ('name', 'need_infra', 'origin', 'origin_v6', 'soa',
                  'api_url')


class MxSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Mx
        fields = ('zone', 'priority', 'name', 'api_url')


class NsSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Ns
        fields = ('zone', 'ns', 'api_url')


class TxtSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Txt
        fields = ('zone', 'field1', 'field2', 'api_url')


class SrvSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Srv
        fields = ('service', 'protocole', 'extension', 'ttl', 'priority',
                  'weight', 'port', 'target', 'api_url')


class InterfaceSerializer(NamespacedHMSerializer):
    mac_address = serializers.CharField()
    active = serializers.BooleanField(source='is_active')

    class Meta:
        model = machines.Interface
        fields = ('ipv4', 'mac_address', 'machine', 'type', 'details',
                  'port_lists', 'active', 'api_url')


class Ipv6ListSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Ipv6List
        fields = ('ipv6', 'interface', 'slaac_ip', 'api_url')


class DomainSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Domain
        fields = ('interface_parent', 'name', 'extension', 'cname',
                  'api_url')


class IpListSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.IpList
        fields = ('ipv4', 'ip_type', 'need_infra', 'api_url')


class ServiceSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Service
        fields = ('service_type', 'min_time_regen', 'regular_time_regen',
                  'servers', 'api_url')


class ServiceLinkSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Service_link
        fields = ('service', 'server', 'last_regen', 'asked_regen',
                  'need_regen', 'api_url')
        extra_kwargs = {
            'api_url': {'view_name': 'servicelink-detail'}
        }


class OuverturePortListSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.OuverturePortList
        fields = ('name', 'tcp_ports_in', 'udp_ports_in', 'tcp_ports_out',
                  'udp_ports_out', 'api_url')


class OuverturePortSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.OuverturePort
        fields = ('begin', 'end', 'port_list', 'protocole', 'io', 'api_url')


# PREFERENCES APP


class OptionalUserSerializer(NamespacedHMSerializer):
    tel_mandatory = serializers.BooleanField(source='is_tel_mandatory')

    class Meta:
        model = preferences.OptionalUser
        fields = ('tel_mandatory', 'user_solde', 'solde_negatif', 'max_solde',
                  'min_online_payment', 'gpg_fingerprint',
                  'all_can_create_club', 'self_adhesion', 'shell_default')


class OptionalMachineSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.OptionalMachine
        fields = ('password_machine', 'max_lambdauser_interfaces',
                  'max_lambdauser_aliases', 'ipv6_mode', 'create_machine',
                  'ipv6')


class OptionalTopologieSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.OptionalTopologie
        fields = ('radius_general_policy', 'vlan_decision_ok',
                  'vlan_decision_nok')


class GeneralOptionSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.GeneralOption
        fields = ('general_message', 'search_display_page',
                  'pagination_number', 'pagination_large_number',
                  'req_expire_hrs', 'site_name', 'email_from', 'GTU_sum_up',
                  'GTU')


class ServiceSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.Service
        fields = ('name', 'url', 'description', 'image', 'api_url')


class AssoOptionSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.AssoOption
        fields = ('name', 'siret', 'adresse1', 'adresse2', 'contact',
                  'telephone', 'pseudo', 'utilisateur_asso', 'payment',
                  'payment_id', 'payment_pass', 'description')


class HomeOptionSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.HomeOption
        fields = ('facebook_url', 'twitter_url', 'twitter_account_name')


class MailMessageOptionSerializer(NamespacedHMSerializer):
    class Meta:
        model = preferences.MailMessageOption
        fields = ('welcome_mail_fr', 'welcome_mail_en')



# TOPOLOGIE APP


class StackSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.Stack
        fields = ('name', 'stack_id', 'details', 'member_id_min',
                  'member_id_max', 'api_url')


class AccessPointSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.AccessPoint
        fields = ('user', 'name', 'active', 'location', 'api_url')


class SwitchSerializer(NamespacedHMSerializer):
    port_amount = serializers.IntegerField(source='number')
    class Meta:
        model = topologie.Switch
        fields = ('user', 'name', 'active', 'port_amount', 'stack',
                  'stack_member_id', 'model', 'switchbay', 'api_url')


class ModelSwitchSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.ModelSwitch
        fields = ('reference', 'constructor', 'api_url')


class ConstructorSwitchSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.ConstructorSwitch
        fields = ('name', 'api_url')


class SwitchBaySerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.SwitchBay
        fields = ('name', 'building', 'info', 'api_url')


class BuildingSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.Building
        fields = ('name', 'api_url')


class SwitchPortSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.Port
        fields = ('switch', 'port', 'room', 'machine_interface', 'related',
                  'radius', 'vlan_force', 'details', 'api_url')
        extra_kwargs = {
            'related': {'view_name': 'switchport-detail'},
            'api_url': {'view_name': 'switchport-detail'}
        }


class RoomSerializer(NamespacedHMSerializer):
    class Meta:
        model = topologie.Room
        fields = ('name', 'details', 'api_url')


# USERS APP


class UserSerializer(NamespacedHMSerializer):
    access = serializers.BooleanField(source='has_access')
    uid = serializers.IntegerField(source='uid_number')

    class Meta:
        model = users.User
        fields = ('name', 'pseudo', 'email', 'school', 'shell', 'comment',
                  'state', 'registered', 'telephone', 'solde', 'access',
                  'end_access', 'uid', 'class_name', 'api_url')
        extra_kwargs = {
            'shell': {'view_name': 'shell-detail'}
        }


class ClubSerializer(NamespacedHMSerializer):
    name = serializers.CharField(source='surname')
    access = serializers.BooleanField(source='has_access')
    uid = serializers.IntegerField(source='uid_number')

    class Meta:
        model = users.Club
        fields = ('name', 'pseudo', 'email', 'school', 'shell', 'comment',
                  'state', 'registered', 'telephone', 'solde', 'room',
                  'access', 'end_access', 'administrators', 'members',
                  'mailing', 'uid', 'api_url')
        extra_kwargs = {
            'shell': {'view_name': 'shell-detail'}
        }


class AdherentSerializer(NamespacedHMSerializer):
    access = serializers.BooleanField(source='has_access')
    uid = serializers.IntegerField(source='uid_number')

    class Meta:
        model = users.Adherent
        fields = ('name', 'surname', 'pseudo', 'email', 'school', 'shell',
                  'comment', 'state', 'registered', 'telephone', 'room',
                  'solde', 'access', 'end_access', 'uid', 'api_url')
        extra_kwargs = {
            'shell': {'view_name': 'shell-detail'}
        }


class ServiceUserSerializer(NamespacedHMSerializer):
    class Meta:
        model = users.ServiceUser
        fields = ('pseudo', 'access_group', 'comment', 'api_url')


class SchoolSerializer(NamespacedHMSerializer):
    class Meta:
        model = users.School
        fields = ('name', 'api_url')


class ListRightSerializer(NamespacedHMSerializer):
    class Meta:
        model = users.ListRight
        fields = ('unix_name', 'gid', 'critical', 'details', 'api_url')


class ShellSerializer(NamespacedHMSerializer):
    class Meta:
        model = users.ListShell
        fields = ('shell', 'api_url')
        extra_kwargs = {
            'api_url': {'view_name': 'shell-detail'}
        }


class BanSerializer(NamespacedHMSerializer):
    active = serializers.BooleanField(source='is_active')

    class Meta:
        model = users.Ban
        fields = ('user', 'raison', 'date_start', 'date_end', 'state',
                  'active', 'api_url')


class WhitelistSerializer(NamespacedHMSerializer):
    active = serializers.BooleanField(source='is_active')

    class Meta:
        model = users.Whitelist
        fields = ('user', 'raison', 'date_start', 'date_end', 'active', 'api_url')


# Services


class ServiceRegenSerializer(NamespacedHMSerializer):
    hostname = serializers.CharField(source='server.domain.name', read_only=True)
    service_name = serializers.CharField(source='service.service_type', read_only=True)
    need_regen = serializers.BooleanField()

    class Meta:
        model = machines.Service_link
        fields = ('hostname', 'service_name', 'need_regen', 'api_url')
        extra_kwargs = {
            'api_url': {'view_name': 'serviceregen-detail'}
        }


# DHCP


class HostMacIpSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(source='domain.name', read_only=True)
    extension = serializers.CharField(source='domain.extension.name', read_only=True)
    mac_address = serializers.CharField(read_only=True)
    ipv4 = serializers.CharField(source='ipv4.ipv4', read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'extension', 'mac_address', 'ipv4')


# DNS


class SOARecordSerializer(SOASerializer):
    class Meta:
        model = machines.SOA
        fields = ('name', 'mail', 'refresh', 'retry', 'expire', 'ttl')


class OriginV4RecordSerializer(IpListSerializer):
    class Meta(IpListSerializer.Meta):
        fields = ('ipv4',)


class OriginV6RecordSerializer(Ipv6ListSerializer):
    class Meta(Ipv6ListSerializer.Meta):
        fields = ('ipv6',)


class NSRecordSerializer(NsSerializer):
    target = serializers.CharField(source='ns.name', read_only=True)

    class Meta(NsSerializer.Meta):
        fields = ('target',)


class MXRecordSerializer(MxSerializer):
    target = serializers.CharField(source='name.name', read_only=True)

    class Meta(MxSerializer.Meta):
        fields = ('target', 'priority')


class TXTRecordSerializer(TxtSerializer):
    class Meta(TxtSerializer.Meta):
        fields = ('field1', 'field2')


class SRVRecordSerializer(SrvSerializer):
    target = serializers.CharField(source='target.name', read_only=True)

    class Meta(SrvSerializer.Meta):
        fields = ('service', 'protocole', 'ttl', 'priority', 'weight', 'port', 'target')


class ARecordSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(source='domain.name', read_only=True)
    ipv4 = serializers.CharField(source='ipv4.ipv4', read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'ipv4')


class AAAARecordSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(source='domain.name', read_only=True)
    ipv6 = Ipv6ListSerializer(many=True, read_only=True)

    class Meta:
        model = machines.Interface
        fields = ('hostname', 'ipv6')


class CNAMERecordSerializer(serializers.ModelSerializer):
    alias = serializers.CharField(source='cname.name', read_only=True)
    hostname = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = machines.Domain
        fields = ('alias', 'hostname')


class DNSZonesSerializer(serializers.ModelSerializer):
    soa = SOARecordSerializer()
    ns_records = NSRecordSerializer(many=True, source='ns_set')
    originv4 = OriginV4RecordSerializer(source='origin')
    originv6 = OriginV6RecordSerializer(source='origin_v6')
    mx_records = MXRecordSerializer(many=True, source='mx_set')
    txt_records = TXTRecordSerializer(many=True, source='txt_set')
    srv_records = SRVRecordSerializer(many=True, source='srv_set')
    a_records = ARecordSerializer(many=True, source='get_associated_a_records')
    aaaa_records = AAAARecordSerializer(many=True, source='get_associated_aaaa_records')
    cname_records = CNAMERecordSerializer(many=True, source='get_associated_cname_records')

    class Meta:
        model = machines.Extension
        fields = ('name', 'soa', 'ns_records', 'originv4', 'originv6',
                  'mx_records', 'txt_records', 'srv_records', 'a_records',
                  'aaaa_records', 'cname_records')


# Mailing


class MailingMemberSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('name', 'pseudo', 'email')

class MailingSerializer(ClubSerializer):
    members = MailingMemberSerializer(many=True)
    admins = MailingMemberSerializer(source='administrators', many=True)

    class Meta(ClubSerializer.Meta):
        fields = ('name', 'members', 'admins')
