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

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt

from re2o.utils import (
    all_has_access,
    all_active_assigned_interfaces,
    filter_active_interfaces
)
from users.models import Club
from machines.models import (
    Service_link,
    Service,
    Interface,
    Domain,
    IpType,
    Mx,
    Ns,
    Txt,
    Srv,
    Extension,
    OuverturePortList,
    OuverturePort
)

from .serializers import (
    ServicesSerializer,
    ServiceLinkSerializer,
    FullInterfaceSerializer,
    DomainSerializer,
    TypeSerializer,
    MxSerializer,
    NsSerializer,
    TxtSerializer,
    SrvSerializer,
    ExtensionSerializer,
    InterfaceSerializer,
    MailingMemberSerializer,
    MailingSerializer
)
from .utils import JSONError, JSONSuccess, accept_method


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def services(_request):
    """The list of the different services and servers couples

    Return:
        GET:
            A JSONSuccess response with a field `data` containing:
            * a list of dictionnaries (one for each service-server couple)
              containing:
              * a field `server`: the server name
              * a field `service`: the service name
              * a field `need_regen`: does the service need a regeneration ?
    """

    service_link = (Service_link.objects.all()
                    .select_related('server__domain')
                    .select_related('service'))
    seria = ServicesSerializer(service_link, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET', 'POST'])
def services_server_service_regen(request, server_name, service_name):
    """The status of a particular service linked to a particular server.
    Mark the service as regenerated if POST used.

    Returns:
        GET:
            A JSONSucess response with a field `data` containing:
            * a field `need_regen`: does the service need a regeneration ?

        POST:
            An empty JSONSuccess response.
    """

    query = Service_link.objects.filter(
        service__in=Service.objects.filter(service_type=service_name),
        server__in=Interface.objects.filter(
            domain__in=Domain.objects.filter(name=server_name)
        )
    )
    if not query:
        return JSONError("This service is not active for this server")

    service = query.first()
    if request.method == 'GET':
        return JSONSuccess({'need_regen': service.need_regen()})
    else:
        service.done_regen()
        return JSONSuccess()


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def services_server(_request, server_name):
    """The list of services attached to a specific server

    Returns:
        GET:
            A JSONSuccess response with a field `data` containing:
            * a list of dictionnaries (one for each service) containing:
              * a field `name`: the name of a service
    """

    query = Service_link.objects.filter(
        server__in=Interface.objects.filter(
            domain__in=Domain.objects.filter(name=server_name)
        )
    )
    if not query:
        return JSONError("This service is not active for this server")

    services_objects = query.all()
    seria = ServiceLinkSerializer(services_objects, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_mac_ip_dns(_request):
    """The list of all active interfaces with all the associated infos
    (MAC, IP, IpType, DNS name and associated zone extension)

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each interface) containing:
              * a field `ipv4` containing:
                * a field `ipv4`: the ip for this interface
                * a field `ip_type`: the name of the IpType of this interface
              * a field `ipv6` containing `null` if ipv6 is deactivated else:
                * a field `ipv6`: the ip for this interface
                * a field `ip_type`: the name of the IpType of this interface
              * a field `mac_address`: the MAC of this interface
              * a field `domain`: the DNS name for this interface
              * a field `extension`: the extension for the DNS zone of this
                interface
    """

    interfaces = all_active_assigned_interfaces(full=True)
    seria = FullInterfaceSerializer(interfaces, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_alias(_request):
    """The list of all the alias used and the DNS info associated

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each alias) containing:
              * a field `name`: the alias used
              * a field `cname`: the target of the alias (real name of the
                interface)
              * a field `cname_entry`: the entry to write in the DNS to have
                the alias
              * a field `extension`: the extension for the DNS zone of this
                interface
    """

    alias = (Domain.objects
             .filter(interface_parent=None)
             .filter(
                 cname__in=Domain.objects.filter(
                     interface_parent__in=Interface.objects.exclude(ipv4=None)
                 )
             )
             .select_related('extension')
             .select_related('cname__extension'))
    seria = DomainSerializer(alias, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def accesspoint_ip_dns(_request):
    """The list of all active interfaces with all the associated infos
    (MAC, IP, IpType, DNS name and associated zone extension)

    Only display access points. Use to gen unifi controler names

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each interface) containing:
              * a field `ipv4` containing:
                * a field `ipv4`: the ip for this interface
                * a field `ip_type`: the name of the IpType of this interface
              * a field `ipv6` containing `null` if ipv6 is deactivated else:
                * a field `ipv6`: the ip for this interface
                * a field `ip_type`: the name of the IpType of this interface
              * a field `mac_address`: the MAC of this interface
              * a field `domain`: the DNS name for this interface
              * a field `extension`: the extension for the DNS zone of this
                interface
    """

    interfaces = (all_active_assigned_interfaces(full=True)
                  .filter(machine__accesspoint__isnull=False))
    seria = FullInterfaceSerializer(interfaces, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_corresp(_request):
    """The list of the IpTypes possible with the infos about each

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each IpType) containing:
              * a field `type`: the name of the type
              * a field `extension`: the DNS extension associated
              * a field `domain_ip_start`: the first ip to use for this type
              * a field `domain_ip_stop`: the last ip to use for this type
              * a field `prefix_v6`: `null` if IPv6 is deactivated else the
                prefix to use
              * a field `ouverture_ports_tcp_in`: the policy for TCP IN ports
              * a field `ouverture_ports_tcp_out`: the policy for TCP OUT ports
              * a field `ouverture_ports_udp_in`: the policy for UDP IN ports
              * a field `ouverture_ports_udp_out`: the policy for UDP OUT ports
    """

    ip_type = IpType.objects.all().select_related('extension')
    seria = TypeSerializer(ip_type, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_mx(_request):
    """The list of MX record to add to the DNS

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each MX record) containing:
              * a field `zone`: the extension for the concerned zone
              * a field `priority`: the priority to use
              * a field `name`: the name of the target
              * a field `mx_entry`: the full entry to add in the DNS for this
                MX record
    """

    mx = (Mx.objects.all()
          .select_related('zone')
          .select_related('name__extension'))
    seria = MxSerializer(mx, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_ns(_request):
    """The list of NS record to add to the DNS

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each NS record) containing:
              * a field `zone`: the extension for the concerned zone
              * a field `ns`: the DNS name for the NS server targeted
              * a field `ns_entry`: the full entry to add in the DNS for this
                NS record
    """

    ns = (Ns.objects
          .exclude(
              ns__in=Domain.objects.filter(
                  interface_parent__in=Interface.objects.filter(ipv4=None)
              )
          )
          .select_related('zone')
          .select_related('ns__extension'))
    seria = NsSerializer(ns, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_txt(_request):
    """The list of TXT record to add to the DNS

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each TXT record) containing:
              * a field `zone`: the extension for the concerned zone
              * a field `field1`: the first field in the record (target)
              * a field `field2`: the second field in the record (value)
              * a field `txt_entry`: the full entry to add in the DNS for this
                TXT record
    """

    txt = Txt.objects.all().select_related('zone')
    seria = TxtSerializer(txt, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_srv(_request):
    """The list of SRV record to add to the DNS

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each SRV record) containing:
              * a field `extension`: the extension for the concerned zone
              * a field `service`: the name of the service concerned
              * a field `protocole`: the name of the protocol to use
              * a field `ttl`: the Time To Live to use
              * a field `priority`: the priority for this service
              * a field `weight`: the weight for same priority entries
              * a field `port`: the port targeted
              * a field `target`: the interface targeted by this service
              * a field `srv_entry`: the full entry to add in the DNS for this
                SRV record
    """

    srv = (Srv.objects.all()
           .select_related('extension')
           .select_related('target__extension'))
    seria = SrvSerializer(srv, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dns_zones(_request):
    """The list of the zones managed

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each zone) containing:
              * a field `name`: the extension for the zone
              * a field `origin`: the server IPv4 for the orgin of the zone
              * a field `origin_v6`: `null` if ipv6 is deactivated else the
                server IPv6 for the origin of the zone
              * a field `soa` containing:
                * a field `mail` containing the mail to contact in case of
                  problem with the zone
                * a field `param` containing the full soa paramters to use
                  in the DNS for this zone
              * a field `zone_entry`: the full entry to add in the DNS for the
                origin of the zone
    """

    zones = Extension.objects.all().select_related('origin')
    seria = ExtensionSerializer(zones, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def firewall_ouverture_ports(_request):
    """The list of the ports authorized to be openned by the firewall

    Returns:
        GET:
            A JSONSuccess response with a `data` field containing:
            * a field `ipv4` containing:
              * a field `tcp_in` containing:
                * a list of port number where ipv4 tcp in should be ok
              * a field `tcp_out` containing:
                * a list of port number where ipv4 tcp ou should be ok
              * a field `udp_in` containing:
                * a list of port number where ipv4 udp in should be ok
              * a field `udp_out` containing:
                * a list of port number where ipv4 udp out should be ok
            * a field `ipv6` containing:
              * a field `tcp_in` containing:
                * a list of port number where ipv6 tcp in should be ok
              * a field `tcp_out` containing:
                * a list of port number where ipv6 tcp ou should be ok
              * a field `udp_in` containing:
                * a list of port number where ipv6 udp in should be ok
              * a field `udp_out` containing:
                * a list of port number where ipv6 udp out should be ok
    """

    r = {'ipv4': {}, 'ipv6': {}}
    for o in (OuverturePortList.objects.all()
              .prefetch_related('ouvertureport_set')
              .prefetch_related('interface_set', 'interface_set__ipv4')):
        pl = {
            "tcp_in": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.TCP,
                    io=OuverturePort.IN
                )
            )),
            "tcp_out": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.TCP,
                    io=OuverturePort.OUT
                )
            )),
            "udp_in": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.UDP,
                    io=OuverturePort.IN
                )
            )),
            "udp_out": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.UDP,
                    io=OuverturePort.OUT
                )
            )),
        }
        for i in filter_active_interfaces(o.interface_set):
            if i.may_have_port_open():
                d = r['ipv4'].get(i.ipv4.ipv4, {})
                d["tcp_in"] = (d.get("tcp_in", set())
                               .union(pl["tcp_in"]))
                d["tcp_out"] = (d.get("tcp_out", set())
                                .union(pl["tcp_out"]))
                d["udp_in"] = (d.get("udp_in", set())
                               .union(pl["udp_in"]))
                d["udp_out"] = (d.get("udp_out", set())
                                .union(pl["udp_out"]))
                r['ipv4'][i.ipv4.ipv4] = d
            if i.ipv6():
                for ipv6 in i.ipv6():
                    d = r['ipv6'].get(ipv6.ipv6, {})
                    d["tcp_in"] = (d.get("tcp_in", set())
                                   .union(pl["tcp_in"]))
                    d["tcp_out"] = (d.get("tcp_out", set())
                                    .union(pl["tcp_out"]))
                    d["udp_in"] = (d.get("udp_in", set())
                                   .union(pl["udp_in"]))
                    d["udp_out"] = (d.get("udp_out", set())
                                    .union(pl["udp_out"]))
                    r['ipv6'][ipv6.ipv6] = d
    return JSONSuccess(r)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dhcp_mac_ip(_request):
    """The list of all active interfaces with all the associated infos
    (MAC, IP, IpType, DNS name and associated zone extension)

    Returns:
        GET:
            A JSON Success response with a field `data` containing:
            * a list of dictionnaries (one for each interface) containing:
              * a field `ipv4` containing:
                * a field `ipv4`: the ip for this interface
                * a field `ip_type`: the name of the IpType of this interface
              * a field `mac_address`: the MAC of this interface
              * a field `domain`: the DNS name for this interface
              * a field `extension`: the extension for the DNS zone of this
                interface
    """

    interfaces = all_active_assigned_interfaces()
    seria = InterfaceSerializer(interfaces, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def mailing_standard(_request):
    """All the available standard mailings.

    Returns:
        GET:
            A JSONSucess response with a field `data` containing:
            * a list of dictionnaries (one for each mailing) containing:
              * a field `name`: the name of a mailing
    """

    return JSONSuccess([
        {'name': 'adherents'}
    ])


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def mailing_standard_ml_members(_request, ml_name):
    """All the members of a specific standard mailing

    Returns:
        GET:
            A JSONSucess response with a field `data` containing:
            * a list if dictionnaries (one for each member) containing:
              * a field `email`:   the email of the member
              * a field `name`:    the name of the member
              * a field `surname`: the surname of the member
              * a field `pseudo`:  the pseudo of the member
    """

    # All with active connextion
    if ml_name == 'adherents':
        members = all_has_access().values('email').distinct()
    # Unknown mailing
    else:
        return JSONError("This mailing does not exist")
    seria = MailingMemberSerializer(members, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def mailing_club(_request):
    """All the available club mailings.

    Returns:
        GET:
            A JSONSucess response with a field `data` containing:
            * a list of dictionnaries (one for each mailing) containing:
              * a field `name` indicating the name of a mailing
    """

    clubs = Club.objects.filter(mailing=True).values('pseudo')
    seria = MailingSerializer(clubs, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def mailing_club_ml_members(_request, ml_name):
    """All the members of a specific club mailing

    Returns:
        GET:
            A JSONSucess response with a field `data` containing:
            * a list if dictionnaries (one for each member) containing:
              * a field `email`:   the email of the member
              * a field `name`:    the name of the member
              * a field `surname`: the surname of the member
              * a field `pseudo`:  the pseudo of the member
    """

    try:
        club = Club.objects.get(mailing=True, pseudo=ml_name)
    except Club.DoesNotExist:
        return JSONError("This mailing does not exist")
    members = club.administrators.all().values('email').distinct()
    seria = MailingMemberSerializer(members, many=True)
    return JSONSuccess(seria.data)
