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
    active = serializers.BooleanField(source='is_active')

    class Meta:
        model = machines.Interface
        fields = ('ipv4', 'mac_address', 'machine', 'type', 'details',
                  'port_lists', 'active', 'api_url')


class Ipv6ListSerializer(NamespacedHMSerializer):
    class Meta:
        model = machines.Ipv6List
        fields = ('ipv6', 'interface', 'slaac_ip', 'date_end',
                  'api_url')


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


# class OptionalUserSerializer(NamespacedHMSerializer):
#     tel_mandatory = serializers.BooleanField(source='is_tel_mandatory')
# 
#     class Meta:
#         model = preferences.OptionalUser
#         fields = ('tel_mandatory', 'user_solde', 'solde_negatif', 'max_solde',
#                   'min_online_payement', 'gpg_fingerprint',
#                   'all_can_create_club', 'self_adhesion', 'shell_default',
#                   'api_url')
# 
# 
# class OptionalMachineSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.OptionalMachine
#         fields = ('password_machine', 'max_lambdauser_interfaces',
#                   'max_lambdauser_aliases', 'ipv6_mode', 'create_machine',
#                   'ipv6', 'api_url')
# 
# 
# class OptionalTopologieSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.OptionalTopologie
#         fields = ('radius_general_policy', 'vlan_decision_ok',
#                   'vlan_decision_no', 'api_url')
# 
# 
# class GeneralOptionSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.GeneralOption
#         fields = ('general_message', 'search_display_page',
#                   'pagination_number', 'pagination_large_number',
#                   'req_expire_hrs', 'site_name', 'email_from', 'GTU_sum_up',
#                   'GTU', 'api_url')
# 
# 
# class ServiceOptionSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.ServiceOption
#         fields = ('name', 'url', 'description', 'image', 'api_url')
# 
# 
# class AssoOptionSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.AssoOption
#         fields = ('name', 'siret', 'adresse1', 'adresse2', 'contact',
#                   'telephone', 'pseudo', 'utilisateur_asso', 'payement',
#                   'payement_id', 'payement_pass', 'description', 'api_url')
# 
# 
# class HomeOptionSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.HomeOption
#         fields = ('facebook_url', 'twitter_url', 'twitter_account_name',
#                   'api_url')
# 
# 
# class MailMessageOptionSerializer(NamespacedHMSerializer):
#     class Meta:
#         model = preferences.MailMessageOption
#         fields = ('welcome_mail_fr', 'welcome_mail_en', 'api_url')



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
        fields = ('port_amount', 'stack', 'stack_member_id', 'model',
                  'switchbay', 'api_url')


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
                  'state', 'registered', 'telephone', 'solde', #'room',
                  'access', 'end_access', 'uid', 'class_name', 'api_url')


class ClubSerializer(NamespacedHMSerializer):
    name = serializers.CharField(source='surname')
    access = serializers.BooleanField(source='has_access')
    uid = serializers.IntegerField(source='uid_number')

    class Meta:
        model = users.Club
        fields = ('name', 'pseudo', 'email', 'school', 'shell', 'comment',
                  'state', 'registered', 'telephone', 'solde', #'room',
                  'access', 'end_access', 'administrators', 'members',
                  'mailing', 'uid', 'api_url')


class AdherentSerializer(NamespacedHMSerializer):
    access = serializers.BooleanField(source='has_access')
    uid = serializers.IntegerField(source='uid_number')

    class Meta:
        model = users.Adherent
        fields = ('name', 'surname', 'pseudo', 'email', 'school', 'shell',
                  'comment', 'state', 'registered', 'telephone', #'room',
                  'solde', 'access', 'end_access', 'uid', 'api_url')


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



# class ServiceLinkSerializer(serializers.ModelSerializer):
#     """ Serializer for the ServiceLink objects """
# 
#     name = serializers.CharField(source='service.service_type')
# 
#     class Meta:
#         model = Service_link
#         fields = ('name',)
# 
# 
# class MailingSerializer(serializers.ModelSerializer):
#     """ Serializer to build Mailing objects """
# 
#     name = serializers.CharField(source='pseudo')
# 
#     class Meta:
#         model = Club
#         fields = ('name',)
# 
# 
# class MailingMemberSerializer(serializers.ModelSerializer):
#     """ Serializer fot the Adherent objects (who belong to a
#     Mailing) """
# 
#     class Meta:
#         model = Adherent
#         fields = ('email',)
# 
# 
# class IpTypeField(serializers.RelatedField):
#     """ Serializer for an IpType object field """
# 
#     def to_representation(self, value):
#         return value.type
# 
#     def to_internal_value(self, data):
#         pass
# 
# 
# class IpListSerializer(serializers.ModelSerializer):
#     """ Serializer for an Ipv4List obejct using the IpType serialization """
# 
#     ip_type = IpTypeField(read_only=True)
# 
#     class Meta:
#         model = IpList
#         fields = ('ipv4', 'ip_type')
# 
# 
# class Ipv6ListSerializer(serializers.ModelSerializer):
#     """ Serializer for an Ipv6List object """
# 
#     class Meta:
#         model = Ipv6List
#         fields = ('ipv6', 'slaac_ip')
# 
# 
# class InterfaceSerializer(serializers.ModelSerializer):
#     """ Serializer for an Interface object. Use SerializerMethodField
#     to get ForeignKey values """
# 
#     ipv4 = IpListSerializer(read_only=True)
#     # TODO : use serializer.RelatedField to avoid duplicate code
#     mac_address = serializers.SerializerMethodField('get_macaddress')
#     domain = serializers.SerializerMethodField('get_dns')
#     extension = serializers.SerializerMethodField('get_interface_extension')
# 
#     class Meta:
#         model = Interface
#         fields = ('ipv4', 'mac_address', 'domain', 'extension')
# 
#     @staticmethod
#     def get_dns(obj):
#         """ The name of the associated  DNS object """
#         return obj.domain.name
# 
#     @staticmethod
#     def get_interface_extension(obj):
#         """ The name of the associated Interface object """
#         return obj.domain.extension.name
# 
#     @staticmethod
#     def get_macaddress(obj):
#         """ The string representation of the associated MAC address """
#         return str(obj.mac_address)
# 
# 
# class FullInterfaceSerializer(serializers.ModelSerializer):
#     """ Serializer for an Interface obejct. Use SerializerMethodField
#     to get ForeignKey values """
# 
#     ipv4 = IpListSerializer(read_only=True)
#     ipv6 = Ipv6ListSerializer(read_only=True, many=True)
#     # TODO : use serializer.RelatedField to avoid duplicate code
#     mac_address = serializers.SerializerMethodField('get_macaddress')
#     domain = serializers.SerializerMethodField('get_dns')
#     extension = serializers.SerializerMethodField('get_interface_extension')
# 
#     class Meta:
#         model = Interface
#         fields = ('ipv4', 'ipv6', 'mac_address', 'domain', 'extension')
# 
#     @staticmethod
#     def get_dns(obj):
#         """ The name of the associated DNS object """
#         return obj.domain.name
# 
#     @staticmethod
#     def get_interface_extension(obj):
#         """ The name of the associated Extension object """
#         return obj.domain.extension.name
# 
#     @staticmethod
#     def get_macaddress(obj):
#         """ The string representation of the associated MAC address """
#         return str(obj.mac_address)
# 
# 
# class ExtensionNameField(serializers.RelatedField):
#     """ Serializer for Extension object field """
# 
#     def to_representation(self, value):
#         return value.name
# 
#     def to_internal_value(self, data):
#         pass
# 
# 
# class TypeSerializer(serializers.ModelSerializer):
#     """ Serializer for an IpType object. Use SerializerMethodField to
#     get ForeignKey values """
# 
#     extension = ExtensionNameField(read_only=True)
#     ouverture_ports_tcp_in = serializers\
#         .SerializerMethodField('get_port_policy_input_tcp')
#     ouverture_ports_tcp_out = serializers\
#         .SerializerMethodField('get_port_policy_output_tcp')
#     ouverture_ports_udp_in = serializers\
#         .SerializerMethodField('get_port_policy_input_udp')
#     ouverture_ports_udp_out = serializers\
#         .SerializerMethodField('get_port_policy_output_udp')
# 
#     class Meta:
#         model = IpType
#         fields = ('type', 'extension', 'domaine_ip_start', 'domaine_ip_stop',
#                   'prefix_v6',
#                   'ouverture_ports_tcp_in', 'ouverture_ports_tcp_out',
#                   'ouverture_ports_udp_in', 'ouverture_ports_udp_out',)
# 
#     @staticmethod
#     def get_port_policy(obj, protocole, io):
#         """ Generic utility function to get the policy for a given
#         port, protocole and IN or OUT """
#         if obj.ouverture_ports is None:
#             return []
#         return map(
#             str,
#             obj.ouverture_ports.ouvertureport_set.filter(
#                 protocole=protocole
#             ).filter(io=io)
#         )
# 
#     def get_port_policy_input_tcp(self, obj):
#         """Renvoie la liste des ports ouverts en entrée tcp"""
#         return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.IN)
# 
#     def get_port_policy_output_tcp(self, obj):
#         """Renvoie la liste des ports ouverts en sortie tcp"""
#         return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.OUT)
# 
#     def get_port_policy_input_udp(self, obj):
#         """Renvoie la liste des ports ouverts en entrée udp"""
#         return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.IN)
# 
#     def get_port_policy_output_udp(self, obj):
#         """Renvoie la liste des ports ouverts en sortie udp"""
#         return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.OUT)
# 
# 
# class ExtensionSerializer(serializers.ModelSerializer):
#     """Serialisation d'une extension : origin_ip et la zone sont
#     des foreign_key donc evalués en get_..."""
#     origin = serializers.SerializerMethodField('get_origin_ip')
#     zone_entry = serializers.SerializerMethodField('get_zone_name')
#     soa = serializers.SerializerMethodField('get_soa_data')
# 
#     class Meta:
#         model = Extension
#         fields = ('name', 'origin', 'origin_v6', 'zone_entry', 'soa')
# 
#     @staticmethod
#     def get_origin_ip(obj):
#         """ The IP of the associated origin for the zone """
#         return obj.origin.ipv4
# 
#     @staticmethod
#     def get_zone_name(obj):
#         """ The name of the associated zone """
#         return str(obj.dns_entry)
# 
#     @staticmethod
#     def get_soa_data(obj):
#         """ The representation of the associated SOA """
#         return {'mail': obj.soa.dns_soa_mail, 'param': obj.soa.dns_soa_param}
# 
# 
# class MxSerializer(serializers.ModelSerializer):
#     """Serialisation d'un MX, evaluation du nom, de la zone
#     et du serveur cible, etant des foreign_key"""
#     name = serializers.SerializerMethodField('get_entry_name')
#     zone = serializers.SerializerMethodField('get_zone_name')
#     mx_entry = serializers.SerializerMethodField('get_mx_name')
# 
#     class Meta:
#         model = Mx
#         fields = ('zone', 'priority', 'name', 'mx_entry')
# 
#     @staticmethod
#     def get_entry_name(obj):
#         """ The name of the DNS MX entry """
#         return str(obj.name)
# 
#     @staticmethod
#     def get_zone_name(obj):
#         """ The name of the associated zone of the MX record """
#         return obj.zone.name
# 
#     @staticmethod
#     def get_mx_name(obj):
#         """ The string representation of the entry to add to the DNS """
#         return str(obj.dns_entry)
# 
# 
# class TxtSerializer(serializers.ModelSerializer):
#     """Serialisation d'un txt : zone cible et l'entrée txt
#     sont evaluées à part"""
#     zone = serializers.SerializerMethodField('get_zone_name')
#     txt_entry = serializers.SerializerMethodField('get_txt_name')
# 
#     class Meta:
#         model = Txt
#         fields = ('zone', 'txt_entry', 'field1', 'field2')
# 
#     @staticmethod
#     def get_zone_name(obj):
#         """ The name of the associated zone """
#         return str(obj.zone.name)
# 
#     @staticmethod
#     def get_txt_name(obj):
#         """ The string representation of the entry to add to the DNS """
#         return str(obj.dns_entry)
# 
# 
# class SrvSerializer(serializers.ModelSerializer):
#     """Serialisation d'un srv : zone cible et l'entrée txt"""
#     extension = serializers.SerializerMethodField('get_extension_name')
#     srv_entry = serializers.SerializerMethodField('get_srv_name')
# 
#     class Meta:
#         model = Srv
#         fields = (
#             'service',
#             'protocole',
#             'extension',
#             'ttl',
#             'priority',
#             'weight',
#             'port',
#             'target',
#             'srv_entry'
#         )
# 
#     @staticmethod
#     def get_extension_name(obj):
#         """ The name of the associated extension """
#         return str(obj.extension.name)
# 
#     @staticmethod
#     def get_srv_name(obj):
#         """ The string representation of the entry to add to the DNS """
#         return str(obj.dns_entry)
# 
# 
# class NsSerializer(serializers.ModelSerializer):
#     """Serialisation d'un NS : la zone, l'entrée ns complète et le serveur
#     ns sont évalués à part"""
#     zone = serializers.SerializerMethodField('get_zone_name')
#     ns = serializers.SerializerMethodField('get_domain_name')
#     ns_entry = serializers.SerializerMethodField('get_text_name')
# 
#     class Meta:
#         model = Ns
#         fields = ('zone', 'ns', 'ns_entry')
# 
#     @staticmethod
#     def get_zone_name(obj):
#         """ The name of the associated zone """
#         return obj.zone.name
# 
#     @staticmethod
#     def get_domain_name(obj):
#         """ The name of the associated NS target """
#         return str(obj.ns)
# 
#     @staticmethod
#     def get_text_name(obj):
#         """ The string representation of the entry to add to the DNS """
#         return str(obj.dns_entry)
# 
# 
# class DomainSerializer(serializers.ModelSerializer):
#     """Serialisation d'un domain, extension, cname sont des foreign_key,
#     et l'entrée complète, sont évalués à part"""
#     extension = serializers.SerializerMethodField('get_zone_name')
#     cname = serializers.SerializerMethodField('get_alias_name')
#     cname_entry = serializers.SerializerMethodField('get_cname_name')
# 
#     class Meta:
#         model = Domain
#         fields = ('name', 'extension', 'cname', 'cname_entry')
# 
#     @staticmethod
#     def get_zone_name(obj):
#         """ The name of the associated zone """
#         return obj.extension.name
# 
#     @staticmethod
#     def get_alias_name(obj):
#         """ The name of the associated alias """
#         return str(obj.cname)
# 
#     @staticmethod
#     def get_cname_name(obj):
#         """ The name of the associated CNAME target """
#         return str(obj.dns_entry)
# 
# 
# class ServicesSerializer(serializers.ModelSerializer):
#     """Evaluation d'un Service, et serialisation"""
#     server = serializers.SerializerMethodField('get_server_name')
#     service = serializers.SerializerMethodField('get_service_name')
#     need_regen = serializers.SerializerMethodField('get_regen_status')
# 
#     class Meta:
#         model = Service_link
#         fields = ('server', 'service', 'need_regen')
# 
#     @staticmethod
#     def get_server_name(obj):
#         """ The name of the associated server """
#         return str(obj.server.domain.name)
# 
#     @staticmethod
#     def get_service_name(obj):
#         """ The name of the service name """
#         return str(obj.service)
# 
#     @staticmethod
#     def get_regen_status(obj):
#         """ The string representation of the regen status """
#         return obj.need_regen()
# 
# 
# class OuverturePortsSerializer(serializers.Serializer):
#     """Serialisation de l'ouverture des ports"""
#     ipv4 = serializers.SerializerMethodField()
#     ipv6 = serializers.SerializerMethodField()
# 
#     def create(self, validated_data):
#         """ Creates a new object based on the un-serialized data.
#         Used to implement an abstract inherited method """
#         pass
# 
#     def update(self, instance, validated_data):
#         """ Updates an object based on the un-serialized data.
#         Used to implement an abstract inherited method """
#         pass
# 
#     @staticmethod
#     def get_ipv4():
#         """ The representation of the policy for the IPv4 addresses """
#         return {
#             i.ipv4.ipv4: {
#                 "tcp_in": [j.tcp_ports_in() for j in i.port_lists.all()],
#                 "tcp_out": [j.tcp_ports_out()for j in i.port_lists.all()],
#                 "udp_in": [j.udp_ports_in() for j in i.port_lists.all()],
#                 "udp_out": [j.udp_ports_out() for j in i.port_lists.all()],
#             }
#             for i in Interface.objects.all() if i.ipv4
#         }
# 
#     @staticmethod
#     def get_ipv6():
#         """ The representation of the policy for the IPv6 addresses """
#         return {
#             i.ipv6: {
#                 "tcp_in": [j.tcp_ports_in() for j in i.port_lists.all()],
#                 "tcp_out": [j.tcp_ports_out()for j in i.port_lists.all()],
#                 "udp_in": [j.udp_ports_in() for j in i.port_lists.all()],
#                 "udp_out": [j.udp_ports_out() for j in i.port_lists.all()],
#             }
#             for i in Interface.objects.all() if i.ipv6
#         }
