# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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
Fonctions de la page d'accueil et diverses fonctions utiles pour tous
les views
"""

from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reversion.models import Version
from django.contrib import messages
from preferences.models import Service
from preferences.models import OptionalUser, GeneralOption, AssoOption
from django.conf import settings
from contributors import contributeurs
import os
import time
from itertools import chain
import users, preferences, cotisations, topologie, machines

def form(ctx, template, request):
    """Form générique, raccourci importé par les fonctions views du site"""
    context = ctx
    context.update(csrf(request))
    return render(request, template, context)


def index(request):
    """Affiche la liste des services sur la page d'accueil de re2o"""
    services = [[], [], []]
    for indice, serv in enumerate(Service.objects.all()):
        services[indice % 3].append(serv)
    return form({'services_urls': services}, 're2o/index.html', request)

#: Binding the corresponding char sequence of history url to re2o models.
HISTORY_BIND = {
    'users' : {
        'user' : users.models.User,
        'ban' : users.models.Ban,
        'whitelist' : users.models.Whitelist,
        'school' : users.models.School,
        'listright' : users.models.ListRight,
        'serviceuser' : users.models.ServiceUser,
        'listshell' : users.models.ListShell,
    },
    'preferences' : {
        'service' : preferences.models.Service,
    },
    'cotisations' : {
        'facture' : cotisations.models.Facture,
        'article' : cotisations.models.Article,
        'paiement' : cotisations.models.Paiement,
        'banque' : cotisations.models.Banque,
    },
    'topologie' : {
        'switch' : topologie.models.Switch,
        'port' : topologie.models.Port,
        'room' : topologie.models.Room,
        'stack' : topologie.models.Stack,
        'modelswitch' : topologie.models.ModelSwitch,
        'constructorswitch' : topologie.models.ConstructorSwitch,
        'accesspoint' : topologie.models.AccessPoint,
    },
    'machines' : {
        'machine' : machines.models.Machine,
        'interface' : machines.models.Interface,
        'domain' : machines.models.Domain,
        'machinetype' : machines.models.MachineType,
        'iptype' : machines.models.IpType,
        'extension' : machines.models.Extension,
        'soa' : machines.models.SOA,
        'mx' : machines.models.Mx,
        'txt' : machines.models.Txt,
        'srv' : machines.models.Srv,
        'ns' : machines.models.Ns,
        'service' : machines.models.Service,
        'vlan' : machines.models.Vlan,
        'nas' : machines.models.Nas,
        'ipv6list' : machines.models.Ipv6List,
    },
}

@login_required
def history(request, application, object_name, object_id):
    """Render history for a model.

    The model is determined using the `HISTORY_BIND` dictionnary if none is
    found, raises a Http404. The view checks if the user is allowed to see the
    history using the `can_view` method of the model.

    Args:
        request: The request sent by the user.
        object_name: Name of the model.
        object_id: Id of the object you want to acces history.

    Returns:
        The rendered page of history if access is granted, else the user is
        redirected to their profile page, with an error message.

    Raises:
        Http404: This kind of models doesn't have history.
    """
    try:
        model = HISTORY_BIND[application][object_name]
    except KeyError as e:
        raise Http404(u"Il n'existe pas d'historique pour ce modèle.")
    object_name_id = object_name + 'id'
    kwargs = {object_name_id: object_id}
    try:
        instance = model.get_instance(**kwargs)
    except model.DoesNotExist:
        messages.error(request, u"Entrée inexistante")
        return redirect(reverse('users:profil',
            kwargs={'userid':str(request.user.id)}
        ))
    can, msg = instance.can_view(request.user)
    if not can:
        messages.error(request, msg or "Vous ne pouvez pas accéder à ce menu")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
        ))
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    reversions = Version.objects.get_for_object(instance)
    if hasattr(instance, 'linked_objects'):
        for related_object in chain(instance.linked_objects()):
            reversions = reversions | Version.objects.get_for_object(related_object)
    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of result
        reversions = paginator.page(paginator.num_pages)
    return render(
        request,
        're2o/history.html',
        {'reversions': reversions, 'object': instance}
    )


def about_page(request):
    option = AssoOption.objects.get()
    n = len(contributeurs)
    contrib_1 = contributeurs[:n//2]
    contrib_2 = contributeurs[n//2:]
    return render(
        request,
        "re2o/about.html",
        {'description': option.description , 'AssoName' : option.name , 'contrib_1' : contrib_1 , 'contrib_2' : contrib_2}
    )

