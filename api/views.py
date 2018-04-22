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

"""api.views

The views for the API app. They should all return JSON data and not fallback on
HTML pages such as the login and index pages for a better integration.
"""

import datetime

from django.conf import settings

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, status


from cotisations.models import (
    Facture,
    Vente,
    Article,
    Banque,
    Paiement,
    Cotisation
)
from machines.models import (
    Machine,
    MachineType,
    IpType,
    Vlan,
    Nas,
    SOA,
    Extension,
    Mx,
    Ns,
    Txt,
    Srv,
    Interface,
    Ipv6List,
    Domain,
    IpList,
    Service,
    Service_link,
    OuverturePortList,
    OuverturePort
)
# from preferences.models import (
#     OptionalUser,
#     OptionalMachine,
#     OptionalTopologie,
#     GeneralOption,
#     AssoOption,
#     HomeOption,
#     MailMessageOption
# )
# # Avoid duplicate names
# from preferences.models import Service as ServiceOption
from users.models import (
    User,
    Club,
    Adherent,
    ServiceUser,
    School,
    ListRight,
    ListShell,
    Ban,
    Whitelist
)

from .serializers import (
    # COTISATIONS APP
    FactureSerializer,
    VenteSerializer,
    ArticleSerializer,
    BanqueSerializer,
    PaiementSerializer,
    CotisationSerializer,
    # MACHINES APP
    MachineSerializer,
    MachineTypeSerializer,
    IpTypeSerializer,
    VlanSerializer,
    NasSerializer,
    SOASerializer,
    ExtensionSerializer,
    MxSerializer,
    NsSerializer,
    TxtSerializer,
    SrvSerializer,
    InterfaceSerializer,
    Ipv6ListSerializer,
    DomainSerializer,
    IpListSerializer,
    ServiceSerializer,
    ServiceLinkSerializer,
    OuverturePortListSerializer,
    OuverturePortSerializer,
    # PREFERENCES APP
    # OptionalUserSerializer,
    # OptionalMachineSerializer,
    # OptionalTopologieSerializer,
    # GeneralOptionSerializer,
    # ServiceOptionSerializer,
    # AssoOptionSerializer,
    # HomeOptionSerializer,
    # MailMessageOptionSerializer,
    # USERS APP
    UserSerializer,
    ClubSerializer,
    AdherentSerializer,
    ServiceUserSerializer,
    SchoolSerializer,
    ListRightSerializer,
    ShellSerializer,
    BanSerializer,
    WhitelistSerializer
)


# COTISATIONS APP


class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer


class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class BanqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banque.objects.all()
    serializer_class = BanqueSerializer


class PaiementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer


class CotisationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cotisation.objects.all()
    serializer_class = CotisationSerializer


# MACHINES APP


class MachineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer


class MachineTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MachineType.objects.all()
    serializer_class = MachineTypeSerializer


class IpTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IpType.objects.all()
    serializer_class = IpTypeSerializer


class VlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vlan.objects.all()
    serializer_class = VlanSerializer


class NasViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Nas.objects.all()
    serializer_class = NasSerializer


class SOAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SOA.objects.all()
    serializer_class = SOASerializer


class ExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer


class MxViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mx.objects.all()
    serializer_class = MxSerializer


class NsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ns.objects.all()
    serializer_class = NsSerializer


class TxtViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Txt.objects.all()
    serializer_class = TxtSerializer


class SrvViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Srv.objects.all()
    serializer_class = SrvSerializer


class InterfaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interface.objects.all()
    serializer_class = InterfaceSerializer


class Ipv6ListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ipv6List.objects.all()
    serializer_class = Ipv6ListSerializer


class DomainViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class IpListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IpList.objects.all()
    serializer_class = IpListSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ServiceLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service_link.objects.all()
    serializer_class = ServiceLinkSerializer


class OuverturePortListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OuverturePortList.objects.all()
    serializer_class = OuverturePortListSerializer


class OuverturePortViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OuverturePort.objects.all()
    serializer_class = OuverturePortSerializer


# PREFERENCES APP

# class OptionalUserViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = OptionalUser.objects.all()
#     serializer_class = OptionalUserSerializer
# 
# 
# class OptionalMachineViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = OptionalMachine.objects.all()
#     serializer_class = OptionalMachineSerializer
# 
# 
# class OptionalTopologieViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = OptionalTopologie.objects.all()
#     serializer_class = OptionalTopologieSerializer
# 
# 
# class GeneralOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = GeneralOption.objects.all()
#     serializer_class = GeneralOptionSerializer
# 
# 
# class ServiceOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = ServiceOption.objects.all()
#     serializer_class = ServiceOptionSerializer
# 
# 
# class AssoOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = AssoOption.objects.all()
#     serializer_class = AssoOptionSerializer
# 
# 
# class HomeOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = HomeOption.objects.all()
#     serializer_class = HomeOptionSerializer
# 
# 
# class MailMessageOptionViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = MailMessageOption.objects.all()
#     serializer_class = MailMessageOptionSerializer


# USER APP


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer


class AdherentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Adherent.objects.all()
    serializer_class = AdherentSerializer


class ServiceUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceUser.objects.all()
    serializer_class = ServiceUserSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class ListRightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ListRight.objects.all()
    serializer_class = ListRightSerializer


class ShellViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ListShell.objects.all()
    serializer_class = ShellSerializer


class BanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ban.objects.all()
    serializer_class = BanSerializer


class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Whitelist.objects.all()
    serializer_class = WhitelistSerializer

# Subclass the standard rest_framework.auth_token.views.ObtainAuthToken
# in order to renew the lease of the token and add expiration time
class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        token_duration = datetime.timedelta(
            seconds=settings.API_TOKEN_DURATION
        )
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if not created and token.created < utc_now - token_duration:
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow()
            token.save()

        return Response({
            'token': token.key,
            'expiration_date': token.created + token_duration
        })

# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def services(_request):
#     """The list of the different services and servers couples
# 
#     Return:
#         GET:
#             A JSONSuccess response with a field `data` containing:
#             * a list of dictionnaries (one for each service-server couple)
#               containing:
#               * a field `server`: the server name
#               * a field `service`: the service name
#               * a field `need_regen`: does the service need a regeneration ?
#     """
# 
#     service_link = (Service_link.objects.all()
#                     .select_related('server__domain')
#                     .select_related('service'))
#     seria = ServicesSerializer(service_link, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET', 'POST'])
# def services_server_service_regen(request, server_name, service_name):
#     """The status of a particular service linked to a particular server.
#     Mark the service as regenerated if POST used.
# 
#     Returns:
#         GET:
#             A JSONSucess response with a field `data` containing:
#             * a field `need_regen`: does the service need a regeneration ?
# 
#         POST:
#             An empty JSONSuccess response.
#     """
# 
#     query = Service_link.objects.filter(
#         service__in=Service.objects.filter(service_type=service_name),
#         server__in=Interface.objects.filter(
#             domain__in=Domain.objects.filter(name=server_name)
#         )
#     )
#     if not query:
#         return JSONError("This service is not active for this server")
# 
#     service = query.first()
#     if request.method == 'GET':
#         return JSONSuccess({'need_regen': service.need_regen()})
#     else:
#         service.done_regen()
#         return JSONSuccess()
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def services_server(_request, server_name):
#     """The list of services attached to a specific server
# 
#     Returns:
#         GET:
#             A JSONSuccess response with a field `data` containing:
#             * a list of dictionnaries (one for each service) containing:
#               * a field `name`: the name of a service
#     """
# 
#     query = Service_link.objects.filter(
#         server__in=Interface.objects.filter(
#             domain__in=Domain.objects.filter(name=server_name)
#         )
#     )
#     if not query:
#         return JSONError("This service is not active for this server")
# 
#     services_objects = query.all()
#     seria = ServiceLinkSerializer(services_objects, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_mac_ip_dns(_request):
#     """The list of all active interfaces with all the associated infos
#     (MAC, IP, IpType, DNS name and associated zone extension)
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each interface) containing:
#               * a field `ipv4` containing:
#                 * a field `ipv4`: the ip for this interface
#                 * a field `ip_type`: the name of the IpType of this interface
#               * a field `ipv6` containing `null` if ipv6 is deactivated else:
#                 * a field `ipv6`: the ip for this interface
#                 * a field `ip_type`: the name of the IpType of this interface
#               * a field `mac_address`: the MAC of this interface
#               * a field `domain`: the DNS name for this interface
#               * a field `extension`: the extension for the DNS zone of this
#                 interface
#     """
# 
#     interfaces = all_active_assigned_interfaces(full=True)
#     seria = FullInterfaceSerializer(interfaces, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_alias(_request):
#     """The list of all the alias used and the DNS info associated
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each alias) containing:
#               * a field `name`: the alias used
#               * a field `cname`: the target of the alias (real name of the
#                 interface)
#               * a field `cname_entry`: the entry to write in the DNS to have
#                 the alias
#               * a field `extension`: the extension for the DNS zone of this
#                 interface
#     """
# 
#     alias = (Domain.objects
#              .filter(interface_parent=None)
#              .filter(
#                  cname__in=Domain.objects.filter(
#                      interface_parent__in=Interface.objects.exclude(ipv4=None)
#                  )
#              )
#              .select_related('extension')
#              .select_related('cname__extension'))
#     seria = DomainSerializer(alias, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def accesspoint_ip_dns(_request):
#     """The list of all active interfaces with all the associated infos
#     (MAC, IP, IpType, DNS name and associated zone extension)
# 
#     Only display access points. Use to gen unifi controler names
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each interface) containing:
#               * a field `ipv4` containing:
#                 * a field `ipv4`: the ip for this interface
#                 * a field `ip_type`: the name of the IpType of this interface
#               * a field `ipv6` containing `null` if ipv6 is deactivated else:
#                 * a field `ipv6`: the ip for this interface
#                 * a field `ip_type`: the name of the IpType of this interface
#               * a field `mac_address`: the MAC of this interface
#               * a field `domain`: the DNS name for this interface
#               * a field `extension`: the extension for the DNS zone of this
#                 interface
#     """
# 
#     interfaces = (all_active_assigned_interfaces(full=True)
#                   .filter(machine__accesspoint__isnull=False))
#     seria = FullInterfaceSerializer(interfaces, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_corresp(_request):
#     """The list of the IpTypes possible with the infos about each
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each IpType) containing:
#               * a field `type`: the name of the type
#               * a field `extension`: the DNS extension associated
#               * a field `domain_ip_start`: the first ip to use for this type
#               * a field `domain_ip_stop`: the last ip to use for this type
#               * a field `prefix_v6`: `null` if IPv6 is deactivated else the
#                 prefix to use
#               * a field `ouverture_ports_tcp_in`: the policy for TCP IN ports
#               * a field `ouverture_ports_tcp_out`: the policy for TCP OUT ports
#               * a field `ouverture_ports_udp_in`: the policy for UDP IN ports
#               * a field `ouverture_ports_udp_out`: the policy for UDP OUT ports
#     """
# 
#     ip_type = IpType.objects.all().select_related('extension')
#     seria = TypeSerializer(ip_type, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_mx(_request):
#     """The list of MX record to add to the DNS
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each MX record) containing:
#               * a field `zone`: the extension for the concerned zone
#               * a field `priority`: the priority to use
#               * a field `name`: the name of the target
#               * a field `mx_entry`: the full entry to add in the DNS for this
#                 MX record
#     """
# 
#     mx = (Mx.objects.all()
#           .select_related('zone')
#           .select_related('name__extension'))
#     seria = MxSerializer(mx, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_ns(_request):
#     """The list of NS record to add to the DNS
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each NS record) containing:
#               * a field `zone`: the extension for the concerned zone
#               * a field `ns`: the DNS name for the NS server targeted
#               * a field `ns_entry`: the full entry to add in the DNS for this
#                 NS record
#     """
# 
#     ns = (Ns.objects
#           .exclude(
#               ns__in=Domain.objects.filter(
#                   interface_parent__in=Interface.objects.filter(ipv4=None)
#               )
#           )
#           .select_related('zone')
#           .select_related('ns__extension'))
#     seria = NsSerializer(ns, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_txt(_request):
#     """The list of TXT record to add to the DNS
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each TXT record) containing:
#               * a field `zone`: the extension for the concerned zone
#               * a field `field1`: the first field in the record (target)
#               * a field `field2`: the second field in the record (value)
#               * a field `txt_entry`: the full entry to add in the DNS for this
#                 TXT record
#     """
# 
#     txt = Txt.objects.all().select_related('zone')
#     seria = TxtSerializer(txt, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_srv(_request):
#     """The list of SRV record to add to the DNS
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each SRV record) containing:
#               * a field `extension`: the extension for the concerned zone
#               * a field `service`: the name of the service concerned
#               * a field `protocole`: the name of the protocol to use
#               * a field `ttl`: the Time To Live to use
#               * a field `priority`: the priority for this service
#               * a field `weight`: the weight for same priority entries
#               * a field `port`: the port targeted
#               * a field `target`: the interface targeted by this service
#               * a field `srv_entry`: the full entry to add in the DNS for this
#                 SRV record
#     """
# 
#     srv = (Srv.objects.all()
#            .select_related('extension')
#            .select_related('target__extension'))
#     seria = SrvSerializer(srv, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dns_zones(_request):
#     """The list of the zones managed
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each zone) containing:
#               * a field `name`: the extension for the zone
#               * a field `origin`: the server IPv4 for the orgin of the zone
#               * a field `origin_v6`: `null` if ipv6 is deactivated else the
#                 server IPv6 for the origin of the zone
#               * a field `soa` containing:
#                 * a field `mail` containing the mail to contact in case of
#                   problem with the zone
#                 * a field `param` containing the full soa paramters to use
#                   in the DNS for this zone
#               * a field `zone_entry`: the full entry to add in the DNS for the
#                 origin of the zone
#     """
# 
#     zones = Extension.objects.all().select_related('origin')
#     seria = ExtensionSerializer(zones, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def firewall_ouverture_ports(_request):
#     """The list of the ports authorized to be openned by the firewall
# 
#     Returns:
#         GET:
#             A JSONSuccess response with a `data` field containing:
#             * a field `ipv4` containing:
#               * a field `tcp_in` containing:
#                 * a list of port number where ipv4 tcp in should be ok
#               * a field `tcp_out` containing:
#                 * a list of port number where ipv4 tcp ou should be ok
#               * a field `udp_in` containing:
#                 * a list of port number where ipv4 udp in should be ok
#               * a field `udp_out` containing:
#                 * a list of port number where ipv4 udp out should be ok
#             * a field `ipv6` containing:
#               * a field `tcp_in` containing:
#                 * a list of port number where ipv6 tcp in should be ok
#               * a field `tcp_out` containing:
#                 * a list of port number where ipv6 tcp ou should be ok
#               * a field `udp_in` containing:
#                 * a list of port number where ipv6 udp in should be ok
#               * a field `udp_out` containing:
#                 * a list of port number where ipv6 udp out should be ok
#     """
# 
#     r = {'ipv4': {}, 'ipv6': {}}
#     for o in (OuverturePortList.objects.all()
#               .prefetch_related('ouvertureport_set')
#               .prefetch_related('interface_set', 'interface_set__ipv4')):
#         pl = {
#             "tcp_in": set(map(
#                 str,
#                 o.ouvertureport_set.filter(
#                     protocole=OuverturePort.TCP,
#                     io=OuverturePort.IN
#                 )
#             )),
#             "tcp_out": set(map(
#                 str,
#                 o.ouvertureport_set.filter(
#                     protocole=OuverturePort.TCP,
#                     io=OuverturePort.OUT
#                 )
#             )),
#             "udp_in": set(map(
#                 str,
#                 o.ouvertureport_set.filter(
#                     protocole=OuverturePort.UDP,
#                     io=OuverturePort.IN
#                 )
#             )),
#             "udp_out": set(map(
#                 str,
#                 o.ouvertureport_set.filter(
#                     protocole=OuverturePort.UDP,
#                     io=OuverturePort.OUT
#                 )
#             )),
#         }
#         for i in filter_active_interfaces(o.interface_set):
#             if i.may_have_port_open():
#                 d = r['ipv4'].get(i.ipv4.ipv4, {})
#                 d["tcp_in"] = (d.get("tcp_in", set())
#                                .union(pl["tcp_in"]))
#                 d["tcp_out"] = (d.get("tcp_out", set())
#                                 .union(pl["tcp_out"]))
#                 d["udp_in"] = (d.get("udp_in", set())
#                                .union(pl["udp_in"]))
#                 d["udp_out"] = (d.get("udp_out", set())
#                                 .union(pl["udp_out"]))
#                 r['ipv4'][i.ipv4.ipv4] = d
#             if i.ipv6():
#                 for ipv6 in i.ipv6():
#                     d = r['ipv6'].get(ipv6.ipv6, {})
#                     d["tcp_in"] = (d.get("tcp_in", set())
#                                    .union(pl["tcp_in"]))
#                     d["tcp_out"] = (d.get("tcp_out", set())
#                                     .union(pl["tcp_out"]))
#                     d["udp_in"] = (d.get("udp_in", set())
#                                    .union(pl["udp_in"]))
#                     d["udp_out"] = (d.get("udp_out", set())
#                                     .union(pl["udp_out"]))
#                     r['ipv6'][ipv6.ipv6] = d
#     return JSONSuccess(r)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def dhcp_mac_ip(_request):
#     """The list of all active interfaces with all the associated infos
#     (MAC, IP, IpType, DNS name and associated zone extension)
# 
#     Returns:
#         GET:
#             A JSON Success response with a field `data` containing:
#             * a list of dictionnaries (one for each interface) containing:
#               * a field `ipv4` containing:
#                 * a field `ipv4`: the ip for this interface
#                 * a field `ip_type`: the name of the IpType of this interface
#               * a field `mac_address`: the MAC of this interface
#               * a field `domain`: the DNS name for this interface
#               * a field `extension`: the extension for the DNS zone of this
#                 interface
#     """
# 
#     interfaces = all_active_assigned_interfaces()
#     seria = InterfaceSerializer(interfaces, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def mailing_standard(_request):
#     """All the available standard mailings.
# 
#     Returns:
#         GET:
#             A JSONSucess response with a field `data` containing:
#             * a list of dictionnaries (one for each mailing) containing:
#               * a field `name`: the name of a mailing
#     """
# 
#     return JSONSuccess([
#         {'name': 'adherents'}
#     ])
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def mailing_standard_ml_members(_request, ml_name):
#     """All the members of a specific standard mailing
# 
#     Returns:
#         GET:
#             A JSONSucess response with a field `data` containing:
#             * a list if dictionnaries (one for each member) containing:
#               * a field `email`:   the email of the member
#               * a field `name`:    the name of the member
#               * a field `surname`: the surname of the member
#               * a field `pseudo`:  the pseudo of the member
#     """
# 
#     # All with active connextion
#     if ml_name == 'adherents':
#         members = all_has_access().values('email').distinct()
#     # Unknown mailing
#     else:
#         return JSONError("This mailing does not exist")
#     seria = MailingMemberSerializer(members, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def mailing_club(_request):
#     """All the available club mailings.
# 
#     Returns:
#         GET:
#             A JSONSucess response with a field `data` containing:
#             * a list of dictionnaries (one for each mailing) containing:
#               * a field `name` indicating the name of a mailing
#     """
# 
#     clubs = Club.objects.filter(mailing=True).values('pseudo')
#     seria = MailingSerializer(clubs, many=True)
#     return JSONSuccess(seria.data)
# 
# 
# @csrf_exempt
# @login_required
# @permission_required('machines.serveur')
# @accept_method(['GET'])
# def mailing_club_ml_members(_request, ml_name):
#     """All the members of a specific club mailing
# 
#     Returns:
#         GET:
#             A JSONSucess response with a field `data` containing:
#             * a list if dictionnaries (one for each member) containing:
#               * a field `email`:   the email of the member
#               * a field `name`:    the name of the member
#               * a field `surname`: the surname of the member
#               * a field `pseudo`:  the pseudo of the member
#     """
# 
#     try:
#         club = Club.objects.get(mailing=True, pseudo=ml_name)
#     except Club.DoesNotExist:
#         return JSONError("This mailing does not exist")
#     members = club.administrators.all().values('email').distinct()
#     seria = MailingMemberSerializer(members, many=True)
#     return JSONSuccess(seria.data)
