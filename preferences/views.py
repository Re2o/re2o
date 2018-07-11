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
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.db import transaction

from reversion import revisions as reversion

from re2o.views import form
from re2o.acl import can_create, can_edit, can_delete, can_delete_set, can_view_all

from .forms import MailContactForm, DelMailContactForm
from .forms import (
    ServiceForm,
    ReminderForm,
    RadiusKeyForm,
    SwitchManagementCredForm
)
from .models import (
    Service,
    MailContact,
    OptionalUser,
    OptionalMachine,
    AssoOption,
    MailMessageOption,
    GeneralOption,
    OptionalTopologie,
    HomeOption,
    Reminder,
    RadiusKey,
    SwitchManagementCred
)
from . import models
from . import forms


def format_options(model):
    """Return a list of tuple for display of settings"""
    model_formated = []
    for field in model._meta.get_fields()[1::2]:
        model_formated.append([(getattr(model, field.name), model._meta.get_field(field.name).help_text)])
    for rank, field in enumerate(model._meta.get_fields()[2::2]):
        model_formated[rank].append((getattr(model, field.name), model._meta.get_field(field.name).help_text))
    return model_formated


@login_required
@can_view_all(OptionalUser, OptionalMachine, OptionalTopologie, GeneralOption,
              AssoOption, MailMessageOption, HomeOption)
def display_options(request):
    """Vue pour affichage des options (en vrac) classé selon les models
    correspondants dans un tableau"""
    useroptions, _created = OptionalUser.objects.get_or_create()
    machineoptions, _created = OptionalMachine.objects.get_or_create()
    topologieoptions, _created = OptionalTopologie.objects.get_or_create()
    generaloptions, _created = GeneralOption.objects.get_or_create()
    assooptions, _created = AssoOption.objects.get_or_create()
    homeoptions, _created = HomeOption.objects.get_or_create()
    mailmessageoptions, _created = MailMessageOption.objects.get_or_create()
    service_list = Service.objects.all()
    mailcontact_list = MailContact.objects.all()
    reminder_list = Reminder.objects.all()
    radiuskey_list = RadiusKey.objects.all()
    switchmanagementcred_list = SwitchManagementCred.objects.all()
    return form({
        'useroptions': useroptions,
        'machineoptions': format_options(machineoptions),
        'topologieoptions': topologieoptions,
        'generaloptions': format_options(generaloptions),
        'assooptions': format_options(assooptions),
        'homeoptions': format_options(homeoptions),
        'mailmessageoptions': format_options(mailmessageoptions),
        'service_list': service_list,
        'reminder_list': reminder_list,
        'mailcontact_list': mailcontact_list,
        'radiuskey_list' : radiuskey_list,
        'switchmanagementcred_list': switchmanagementcred_list,  
        }, 'preferences/display_preferences.html', request)


@login_required
def edit_options(request, section):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, 'Edit' + section + 'Form', None)
    if not (model or form_instance):
        messages.error(request, "Objet  inconnu")
        return redirect(reverse('preferences:display-options'))

    options_instance, _created = model.objects.get_or_create()
    can, msg = options_instance.can_edit(request.user)
    if not can:
        messages.error(request, msg or "Vous ne pouvez pas éditer cette\
                   option.")
        return redirect(reverse('index'))
    options = form_instance(
        request.POST or None,
        request.FILES or None,
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


@login_required
@can_create(Service)
def add_service(request):
    """Ajout d'un service de la page d'accueil"""
    service = ServiceForm(request.POST or None, request.FILES or None)
    if service.is_valid():
        service.save()
        messages.success(request, "Ce service a été ajouté")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': service, 'action_name': 'Ajouter'},
        'preferences/preferences.html',
        request
        )


@login_required
@can_edit(Service)
def edit_service(request, service_instance, **_kwargs):
    """Edition des services affichés sur la page d'accueil"""
    service = ServiceForm(
        request.POST or None,
        request.FILES or None,
        instance=service_instance
    )
    if service.is_valid():
        service.save()
        messages.success(request, "Service modifié")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': service, 'action_name': 'Editer'},
        'preferences/preferences.html',
        request
    )

@login_required
@can_delete(Service)
def del_service(request, service_instance, **_kwargs):
    """Destruction d'un service"""
    if request.method == "POST":
        service_instance.delete()
        messages.success(request, "Le service a été détruit")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': service_instance, 'objet_name': 'service'},
        'preferences/delete.html',
        request
        )

@login_required
@can_create(Reminder)
def add_reminder(request):
    """Ajout d'un rappel"""
    reminder = ReminderForm(request.POST or None)
    if reminder.is_valid():
        reminder.save()
        messages.success(request, "Ce rappel a été ajouté")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': reminder, 'action_name': 'Ajouter'},
        'preferences/preferences.html',
        request
        )

@can_edit(Reminder)
def edit_reminder(request, reminder_instance, **_kwargs):
    """Edition des rappels"""
    reminder = ReminderForm(request.POST or None, instance=reminder_instance)
    if reminder.is_valid():
        reminder.save()
        messages.success(request, "Service modifié")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': reminder, 'action_name': 'Editer'},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete(Reminder)
def del_reminder(request, reminder_instance, **_kwargs):
    """Destruction d'un reminder"""
    if request.method == "POST":
        reminder_instance.delete()
        messages.success(request, "Le reminder a été détruit")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': reminder_instance, 'objet_name': 'reminder'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(RadiusKey)
def add_radiuskey(request):
    """Ajout d'une clef radius"""
    radiuskey = RadiusKeyForm(request.POST or None)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, "Cette clef a été ajouté")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': radiuskey, 'action_name': 'Ajouter'},
        'preferences/preferences.html',
        request
        )

@can_edit(RadiusKey)
def edit_radiuskey(request, radiuskey_instance, **_kwargs):
    """Edition des clefs radius"""
    radiuskey = RadiusKeyForm(request.POST or None, instance=radiuskey_instance)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, "Radiuskey modifié")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': radiuskey, 'action_name': 'Editer'},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete(RadiusKey)
def del_radiuskey(request, radiuskey_instance, **_kwargs):
    """Destruction d'un radiuskey"""
    if request.method == "POST":
        radiuskey_instance.delete()
        messages.success(request, "La radiuskey a été détruite")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': radiuskey_instance, 'objet_name': 'radiuskey'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(SwitchManagementCred)
def add_switchmanagementcred(request):
    """Ajout de creds de management"""
    switchmanagementcred = SwitchManagementCredForm(request.POST or None)
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, "Ces creds ont été ajoutés")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': switchmanagementcred, 'action_name': 'Ajouter'},
        'preferences/preferences.html',
        request
        )

@can_edit(SwitchManagementCred)
def edit_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """Edition des creds de management"""
    switchmanagementcred = SwitchManagementCredForm(request.POST or None, instance=switchmanagementcred_instance)
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, "Creds de managament modifié")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': switchmanagementcred, 'action_name': 'Editer'},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete(SwitchManagementCred)
def del_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """Destruction d'un switchmanagementcred"""
    if request.method == "POST":
        switchmanagementcred_instance.delete()
        messages.success(request, "Ce switchmanagementcred a été détruit")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': switchmanagementcred_instance, 'objet_name': 'switchmanagementcred'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(MailContact)
def add_mailcontact(request):
    """Ajout d'une adresse de contact"""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None
    )
    if mailcontact.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mailcontact.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cette adresse a été ajoutée")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact, 'action_name': 'Ajouter'},
        'preferences/preferences.html',
        request
    )


@login_required
@can_edit(MailContact)
def edit_mailcontact(request, mailcontact_instance, **_kwargs):
    """Edition des adresses de contacte affichées"""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None,
        instance=mailcontact_instance
    )
    if mailcontact.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mailcontact.save()
            reversion.set_user(request.user)
            reversion.set_comment("Modification")
        messages.success(request, "Adresse modifiée")
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact, 'action_name': 'Editer'},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete_set(MailContact)
def del_mailcontact(request, instances):
    """Suppression d'une adresse de contact"""
    mailcontacts = DelMailContactForm(
        request.POST or None,
        instances=instances
    )
    if mailcontacts.is_valid():
        mailcontacts_dels = mailcontacts.cleaned_data['mailcontacts']
        for mailcontacts_del in mailcontacts_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    mailcontacts_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'adresse a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le service\
                suivant %s ne peut être supprimé" % mailcontacts_del)
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontacts, 'action_name': 'Supprimer'},
        'preferences/preferences.html',
        request
    )

