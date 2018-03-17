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
