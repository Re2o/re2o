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
from django.utils.translation import ugettext as _

from reversion import revisions as reversion

from re2o.views import form
from re2o.acl import can_create, can_edit, can_delete, can_view_all

from .forms import (
    ServiceForm, DelServiceForm, MailContactForm, DelMailContactForm, ReminderForm, ReminderForm
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
    HomeOption
)
from . import models
from . import forms


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
    return form({
        'useroptions': useroptions,
        'machineoptions': machineoptions,
        'topologieoptions': topologieoptions,
        'generaloptions': generaloptions,
        'assooptions': assooptions,
        'homeoptions': homeoptions,
        'mailmessageoptions': mailmessageoptions,
        'service_list': service_list,
        'mailcontact_list': mailcontact_list
        }, 'preferences/display_preferences.html', request)


@login_required
def edit_options(request, section):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, 'Edit' + section + 'Form', None)
    if not (model or form_instance):
        messages.error(request, _("Unknown object"))
        return redirect(reverse('preferences:display-options'))

    options_instance, _created = model.objects.get_or_create()
    can, msg = options_instance.can_edit(request.user)
    if not can:
        messages.error(request, msg or _("You don't have the right to edit"
                                         " this option."))
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
                "Field(s) edited: %s" % ', '.join(
                    field for field in options.changed_data
                )
            )
            messages.success(request, _("The preferences were edited."))
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
        {'preferenceform': service, 'action_name': _("Add a service")},
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
        {'preferenceform': service, 'action_name': _("Edit")},
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

@login_required
@can_delete_set(Service)
def del_service(request, instances):
    """Suppression d'un service de la page d'accueil"""
    services = DelServiceForm(request.POST or None, instances=instances)
    if services.is_valid():
        services_dels = services.cleaned_data['services']
        for services_del in services_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    services_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, _("The service was deleted."))
            except ProtectedError:
                messages.error(request, _("Error: the service %s can't be"
                                          " deleted.") % services_del)
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': services, 'action_name': _("Delete")},
        'preferences/preferences.html',
        request
    )


@login_required
@can_create(MailContact)
def add_mailcontact(request):
    """Add a contact email adress."""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None
    )
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was created."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact,
            'action_name': _("Add a contact email address")},
        'preferences/preferences.html',
        request
        )


@login_required
@can_edit(MailContact)
def edit_mailcontact(request, mailcontact_instance, **_kwargs):
    """Edit contact email adress."""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None,
        instance=mailcontact_instance
    )
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact, 'action_name': _("Edit")},

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
@can_delete_set(MailContact)
def del_mailcontact(request, instances):
    """Delete an email adress"""
    mailcontacts = DelMailContactForm(
        request.POST or None,
        instances=instances
    )
    if mailcontacts.is_valid():
        mailcontacts_dels = mailcontacts.cleaned_data['mailcontacts']
        for mailcontacts_del in mailcontacts_dels:
            mailcontacts_del.delete()
            messages.success(request,
                    _("The contact email adress was deleted."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontacts, 'action_name': _("Delete")},
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


