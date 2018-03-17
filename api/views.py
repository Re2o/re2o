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

from re2o.utils import all_has_access, all_active_assigned_interfaces

from users.models import Club
from machines.models import Service_link, Service, Interface, Domain

from .serializers import *
from .utils import JSONError, JSONSuccess, accept_method


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def services(request):
    """The list of the different services and servers couples

    Return:
        GET:
            A JSONSuccess response with a field `data` containing:
            * a list of dictionnaries (one for each service-server couple) containing:
              * a field `server`: the server name
              * a field `service`: the service name
              * a field `need_regen`: does the service need a regeneration ?
    """
    service_link = Service_link.objects.all().select_related('server__domain').select_related('service')
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
def services_server(request, server_name):
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
    
    services = query.all()
    seria = ServiceLinkSerializer(services, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def dhcp_mac_ip(request):
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
              * a field `extension`: the extension for the DNS zone of this interface
    """
    interfaces = all_active_assigned_interfaces()
    seria = InterfaceSerializer(interfaces, many=True)
    return JSONSuccess(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
@accept_method(['GET'])
def mailing_standard(request):
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
def mailing_standard_ml_members(request):
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
def mailing_club(request):
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
def mailing_club_ml_members(request):
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
