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

# App de gestion des machines pour re2o
# Gabriel Détraz, Augustin Lemesle
# Gplv2
"""
Vue d'affichage, et de modification des réglages (réglages machine,
topologie, users, service...)
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.db import transaction

from reversion.models import Version
from reversion import revisions as reversion

from re2o.views import form
from .forms import ServiceForm, DelServiceForm
from .models import Service, OptionalUser, OptionalMachine, AssoOption
from .models import MailMessageOption, GeneralOption, OptionalTopologie
from . import models
from . import forms


@login_required
@permission_required('cableur')
def display_options(request):
    """Vue pour affichage des options (en vrac) classé selon les models
    correspondants dans un tableau"""
    useroptions, _created = OptionalUser.objects.get_or_create()
    machineoptions, _created = OptionalMachine.objects.get_or_create()
    topologieoptions, _created = OptionalTopologie.objects.get_or_create()
    generaloptions, _created = GeneralOption.objects.get_or_create()
    assooptions, _created = AssoOption.objects.get_or_create()
    mailmessageoptions, _created = MailMessageOption.objects.get_or_create()
    service_list = Service.objects.all()
    return form({
        'useroptions': useroptions,
        'machineoptions': machineoptions,
        'topologieoptions': topologieoptions,
        'generaloptions': generaloptions,
        'assooptions': assooptions,
        'mailmessageoptions': mailmessageoptions,
        'service_list': service_list
        }, 'preferences/display_preferences.html', request)


@login_required
@permission_required('admin')
def edit_options(request, section):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, 'Edit' + section + 'Form', None)
    if model and form:
        options_instance, _created = model.objects.get_or_create()
        options = form_instance(
            request.POST or None,
            instance=options_instance
        )
        if options.is_valid():
            with transaction.atomic(), reversion.create_revision():
                options.save()
                reversion.set_user(request.user)
                reversion.set_comment(
                    "Champs modifié(s) : %s" % ', '.join(
                        field for field in options.changed_data
                    )
                )
            messages.success(request, "Préférences modifiées")
            return redirect(reverse('preferences:display-options'))
        return form(
            {'options': options},
            'preferences/edit_preferences.html',
            request
            )
    else:
        messages.error(request, "Objet  inconnu")
        return redirect(reverse('preferences:display-options'))


@login_required
@permission_required('admin')
def add_services(request):
    """Ajout d'un service de la page d'accueil"""
    services = ServiceForm(request.POST or None)
    if services.is_valid():
        with transaction.atomic(), reversion.create_revision():
            services.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Ce service a été ajouté")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': services},
        'preferences/preferences.html',
        request
        )


@login_required
@permission_required('admin')
def edit_services(request, servicesid):
    """Edition des services affichés sur la page d'accueil"""
    try:
        services_instance = Service.objects.get(pk=servicesid)
    except Service.DoesNotExist:
        messages.error(request, u"Entrée inexistante")
        return redirect(reverse('preferences:display-options'))
    services = ServiceForm(request.POST or None, instance=services_instance)
    if services.is_valid():
        with transaction.atomic(), reversion.create_revision():
            services.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Champs modifié(s) : %s" % ', '.join(
                    field for field in services.changed_data
                    )
            )
        messages.success(request, "Service modifié")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': services},
        'preferences/preferences.html',
        request
    )


@login_required
@permission_required('admin')
def del_services(request):
    """Suppression d'un service de la page d'accueil"""
    services = DelServiceForm(request.POST or None)
    if services.is_valid():
        services_dels = services.cleaned_data['services']
        for services_del in services_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    services_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le services a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le service\
                suivant %s ne peut être supprimé" % services_del)
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': services},
        'preferences/preferences.html',
        request
    )


@login_required
@permission_required('cableur')
def history(request, object_name, object_id):
    """Historique de creation et de modification d'un service affiché sur
    la page d'accueil"""
    if object_name == 'service':
        try:
            object_instance = Service.objects.get(pk=object_id)
        except Service.DoesNotExist:
            messages.error(request, "Service inexistant")
            return redirect(reverse('preferences:display-options'))
    options, _created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 're2o/history.html', {
        'reversions': reversions,
        'object': object_instance
        })
