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


from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max, ProtectedError
from django.db import IntegrityError
from django.core.mail import send_mail
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import transaction

from reversion.models import Version
from reversion import revisions as reversion

from .forms import ServiceForm, DelServiceForm
from .models import Service, OptionalUser, OptionalMachine, AssoOption, MailMessageOption, GeneralOption, OptionalTopologie 
from . import models
from . import forms

def form(ctx, template, request):
    c = ctx
    c.update(csrf(request))
    return render(request, template, c)


@login_required
@permission_required('cableur')
def display_options(request):
    useroptions, created = OptionalUser.objects.get_or_create()
    machineoptions, created = OptionalMachine.objects.get_or_create()
    topologieoptions, created = OptionalTopologie.objects.get_or_create()
    generaloptions, created = GeneralOption.objects.get_or_create()
    assooptions, created = AssoOption.objects.get_or_create()
    mailmessageoptions, created = MailMessageOption.objects.get_or_create()
    service_list = Service.objects.all()
    return form({'useroptions': useroptions, 'machineoptions': machineoptions, 'topologieoptions': topologieoptions, 'generaloptions': generaloptions, 'assooptions' : assooptions, 'mailmessageoptions' : mailmessageoptions, 'service_list':service_list}, 'preferences/display_preferences.html', request)

@login_required
@permission_required('admin')
def edit_options(request, section):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, 'Edit' + section + 'Form', None)
    if model and form:
        options_instance, created = model.objects.get_or_create()
        options = form_instance(request.POST or None, instance=options_instance)
        if options.is_valid():
            with transaction.atomic(), reversion.create_revision():
                options.save()
                reversion.set_user(request.user)
                reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in options.changed_data))
            messages.success(request, "Préférences modifiées")
            return redirect("/preferences/")
        return form({'options': options}, 'preferences/edit_preferences.html', request)
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/preferences/")

@login_required
@permission_required('admin')
def add_services(request):
    services = ServiceForm(request.POST or None)
    if services.is_valid():
        with transaction.atomic(), reversion.create_revision():
            services.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement ns a été ajouté")
        return redirect("/preferences/")
    return form({'preferenceform': services}, 'preferences/preferences.html', request)

@login_required
@permission_required('admin')
def edit_services(request, servicesid):
    try:
        services_instance = Service.objects.get(pk=servicesid)
    except Service.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect("/preferences/")
    services = ServiceForm(request.POST or None, instance=services_instance)
    if services.is_valid():
        with transaction.atomic(), reversion.create_revision():
            services.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in services.changed_data))
        messages.success(request, "Service modifié")
        return redirect("/preferences/")
    return form({'preferenceform': services}, 'preferences/preferences.html', request)

@login_required
@permission_required('admin')
def del_services(request):
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
                messages.error(request, "Erreur le service suivant %s ne peut être supprimé" % services_del)
        return redirect("/preferences/")
    return form({'preferenceform': services}, 'preferences/preferences.html', request)

@login_required
@permission_required('cableur')
def history(request, object, id):
    if object == 'service':
        try:
             object_instance = Service.objects.get(pk=id)
        except Service.DoesNotExist:
             messages.error(request, "Service inexistant")
             return redirect("/preferences/")
    options, created = GeneralOption.objects.get_or_create()
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
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})
