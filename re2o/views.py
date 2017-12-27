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
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reversion.models import Version
from django.contrib import messages
from preferences.models import Service
from preferences.models import OptionalUser, GeneralOption
import users, preferences, cotisations

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


HISTORY_BIND = {
    'user' : users.models.User,
    'ban' : users.models.Ban,
    'whitelist' : users.models.Whitelist,
    'school' : users.models.School,
    'listright' : users.models.ListRight,
    'serviceuser' : users.models.ServiceUser,
    'service' : preferences.models.Service,
    'facture' : cotisations.models.Facture,
    'article' : cotisations.models.Article,
    'paiement' : cotisations.models.Paiement,
    'banque' : cotisations.models.Banque,
}

@login_required
def history(request, object_name, object_id):
    """ Affichage de l'historique"""
    try:
        model = HISTORY_BIND[object_name]
    except KeyError as e:
        raise Http404(u"Il n'existe pas d'historique pour ce modèle.")
    try:
        instance = model.get_instance(object_id)
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
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(instance)
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

