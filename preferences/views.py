# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
Views to display and edit settings (preferences of machines, users, topology,
services etc.)
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

from importlib import import_module
from re2o.settings_local import OPTIONNAL_APPS_RE2O
from re2o.views import form
from re2o.acl import (
    can_create,
    can_edit,
    can_delete_set,
    can_view_all,
    can_delete,
    acl_error_message,
)

from .forms import MailContactForm, DelMailContactForm
from .forms import (
    ServiceForm,
    ReminderForm,
    RadiusKeyForm,
    SwitchManagementCredForm,
    DocumentTemplateForm,
    DelDocumentTemplateForm,
    RadiusAttributeForm,
    DelRadiusAttributeForm,
    MandateForm,
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
    SwitchManagementCred,
    RadiusOption,
    CotisationsOption,
    DocumentTemplate,
    RadiusAttribute,
    Mandate,
)
from . import models
from . import forms


def edit_options_template_function(request, section, forms, models):
    """View used to edit general preferences."""
    model = getattr(models, section, None)
    form_instance = getattr(forms, "Edit" + section + "Form", None)
    if not (model or form_instance):
        messages.error(request, _("Unknown object."))
        return redirect(reverse("preferences:display-options"))

    options_instance, _created = model.objects.get_or_create()
    _is_allowed_to_edit, msg, permissions = options_instance.can_edit(request.user)
    if not _is_allowed_to_edit:
        messages.error(request, acl_error_message(msg, permissions))
        return redirect(reverse("index"))
    options = form_instance(
        request.POST or None, request.FILES or None, instance=options_instance
    )
    if options.is_valid():
        with transaction.atomic(), reversion.create_revision():
            options.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Field(s) edited: %s"
                % ", ".join(field for field in options.changed_data)
            )
            messages.success(request, _("The preferences were edited."))
        return redirect(reverse("preferences:display-options"))
    return form({"options": options}, "preferences/edit_preferences.html", request)


@login_required
@can_view_all(
    OptionalUser,
    OptionalMachine,
    OptionalTopologie,
    GeneralOption,
    AssoOption,
    MailMessageOption,
    HomeOption,
)
def display_options(request):
    """View used to display preferences sorted by model."""
    useroptions, _created = OptionalUser.objects.get_or_create()
    machineoptions, _created = OptionalMachine.objects.get_or_create()
    topologieoptions, _created = OptionalTopologie.objects.get_or_create()
    generaloptions, _created = GeneralOption.objects.get_or_create()
    assooptions, _created = AssoOption.objects.get_or_create()
    mandate_list = Mandate.objects.order_by("start_date")
    homeoptions, _created = HomeOption.objects.get_or_create()
    mailmessageoptions, _created = MailMessageOption.objects.get_or_create()
    service_list = Service.objects.all()
    mailcontact_list = MailContact.objects.all()
    reminder_list = Reminder.objects.all()
    radiuskey_list = RadiusKey.objects.all()
    switchmanagementcred_list = SwitchManagementCred.objects.all()
    radiusoptions, _ = RadiusOption.objects.get_or_create()
    radius_attributes = RadiusAttribute.objects.all()
    cotisationsoptions, _created = CotisationsOption.objects.get_or_create()
    document_template_list = DocumentTemplate.objects.order_by("name")

    optionnal_apps = [import_module(app) for app in OPTIONNAL_APPS_RE2O]
    optionnal_templates_list = [
        app.preferences.views.aff_preferences(request)
        for app in optionnal_apps
        if hasattr(app.preferences.views, "aff_preferences")
    ]

    return form(
        {
            "useroptions": useroptions,
            "machineoptions": machineoptions,
            "topologieoptions": topologieoptions,
            "generaloptions": generaloptions,
            "assooptions": assooptions,
            "mandate_list": mandate_list,
            "homeoptions": homeoptions,
            "mailmessageoptions": mailmessageoptions,
            "service_list": service_list,
            "mailcontact_list": mailcontact_list,
            "reminder_list": reminder_list,
            "radiuskey_list": radiuskey_list,
            "switchmanagementcred_list": switchmanagementcred_list,
            "radiusoptions": radiusoptions,
            "radius_attributes": radius_attributes,
            "cotisationsoptions": cotisationsoptions,
            "optionnal_templates_list": optionnal_templates_list,
            "document_template_list": document_template_list,
        },
        "preferences/display_preferences.html",
        request,
    )


@login_required
def edit_options(request, section):
    return edit_options_template_function(request, section, forms, models)


@login_required
@can_create(Service)
def add_service(request):
    """View used to add services displayed on the home page."""
    service = ServiceForm(request.POST or None, request.FILES or None)
    if service.is_valid():
        service.save()
        messages.success(request, _("The service was added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": service, "action_name": _("Add")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(Service)
def edit_service(request, service_instance, **_kwargs):
    """View used to edit services displayed on the home page."""
    service = ServiceForm(
        request.POST or None, request.FILES or None, instance=service_instance
    )
    if service.is_valid():
        service.save()
        messages.success(request, _("The service was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": service, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(Service)
def del_service(request, service_instance, **_kwargs):
    """View used to delete services displayed on the home page."""
    if request.method == "POST":
        service_instance.delete()
        messages.success(request, _("The service was deleted."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"objet": service_instance, "objet_name": _("service")},
        "preferences/delete.html",
        request,
    )


@login_required
@can_create(Reminder)
def add_reminder(request):
    """View used to add reminders."""
    reminder = ReminderForm(request.POST or None, request.FILES or None)
    if reminder.is_valid():
        reminder.save()
        messages.success(request, _("The reminder was added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": reminder, "action_name": _("Add")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(Reminder)
def edit_reminder(request, reminder_instance, **_kwargs):
    """View used to edit reminders."""
    reminder = ReminderForm(
        request.POST or None, request.FILES or None, instance=reminder_instance
    )
    if reminder.is_valid():
        reminder.save()
        messages.success(request, _("The reminder was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": reminder, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(Reminder)
def del_reminder(request, reminder_instance, **_kwargs):
    """View used to delete reminders."""
    if request.method == "POST":
        reminder_instance.delete()
        messages.success(request, _("The reminder was deleted."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"objet": reminder_instance, "objet_name": _("reminder")},
        "preferences/delete.html",
        request,
    )


@login_required
@can_create(RadiusKey)
def add_radiuskey(request):
    """View used to add RADIUS keys."""
    radiuskey = RadiusKeyForm(request.POST or None)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, _("The RADIUS key was added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": radiuskey, "action_name": _("Add")},
        "preferences/preferences.html",
        request,
    )


@can_edit(RadiusKey)
def edit_radiuskey(request, radiuskey_instance, **_kwargs):
    """View used to edit RADIUS keys."""
    radiuskey = RadiusKeyForm(request.POST or None, instance=radiuskey_instance)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, _("The RADIUS key was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": radiuskey, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(RadiusKey)
def del_radiuskey(request, radiuskey_instance, **_kwargs):
    """View used to delete RADIUS keys."""
    if request.method == "POST":
        try:
            radiuskey_instance.delete()
            messages.success(request, _("The RADIUS key was deleted."))
        except ProtectedError:
            messages.error(
                request,
                _(
                    "The RADIUS key is assigned to at least"
                    " one switch, you can't delete it."
                ),
            )
        return redirect(reverse("preferences:display-options"))
    return form(
        {"objet": radiuskey_instance, "objet_name": _("RADIUS key")},
        "preferences/delete.html",
        request,
    )


@login_required
@can_create(SwitchManagementCred)
def add_switchmanagementcred(request):
    """Ajout de creds de management"""
    """View used to add switch management credentials."""
    switchmanagementcred = SwitchManagementCredForm(request.POST or None)
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, _("The switch management credentials were added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": switchmanagementcred, "action_name": _("Add"),},
        "preferences/preferences.html",
        request,
    )


@can_edit(SwitchManagementCred)
def edit_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """View used to edit switch management credentials."""
    switchmanagementcred = SwitchManagementCredForm(
        request.POST or None, instance=switchmanagementcred_instance
    )
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, _("The switch management credentials were edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": switchmanagementcred, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(SwitchManagementCred)
def del_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """View used to delete switch management credentials."""
    if request.method == "POST":
        try:
            switchmanagementcred_instance.delete()
            messages.success(
                request, _("The switch management credentials were deleted.")
            )
        except ProtectedError:
            messages.error(
                request,
                _(
                    "The switch management credentials are"
                    " assigned to at least one switch, you"
                    " can't delete them."
                ),
            )
        return redirect(reverse("preferences:display-options"))
    return form(
        {
            "objet": switchmanagementcred_instance,
            "objet_name": _("switch management credentials"),
        },
        "preferences/delete.html",
        request,
    )


@login_required
@can_create(MailContact)
def add_mailcontact(request):
    """View used to add contact email addresses."""
    mailcontact = MailContactForm(request.POST or None, request.FILES or None)
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was created."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": mailcontact, "action_name": _("Add"),},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(MailContact)
def edit_mailcontact(request, mailcontact_instance, **_kwargs):
    """View used to edit contact email addresses."""
    mailcontact = MailContactForm(
        request.POST or None, request.FILES or None, instance=mailcontact_instance
    )
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": mailcontact, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete_set(MailContact)
def del_mailcontact(request, instances):
    """View used to delete one or several contact email addresses."""
    mailcontacts = DelMailContactForm(request.POST or None, instances=instances)
    if mailcontacts.is_valid():
        mailcontacts_dels = mailcontacts.cleaned_data["mailcontacts"]
        for mailcontacts_del in mailcontacts_dels:
            mailcontacts_del.delete()
            messages.success(request, _("The contact email adress was deleted."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": mailcontacts, "action_name": _("Delete")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_create(DocumentTemplate)
def add_document_template(request):
    """View used to add document templates."""
    document_template = DocumentTemplateForm(
        request.POST or None, request.FILES or None
    )
    if document_template.is_valid():
        document_template.save()
        messages.success(request, _("The document template was created."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {
            "preferenceform": document_template,
            "action_name": _("Add"),
            "title": _("New document template"),
        },
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(DocumentTemplate)
def edit_document_template(request, document_template_instance, **_kwargs):
    """View used to edit document templates."""
    document_template = DocumentTemplateForm(
        request.POST or None, request.FILES or None, instance=document_template_instance
    )
    if document_template.is_valid():
        if document_template.changed_data:
            document_template.save()
            messages.success(request, _("The document template was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {
            "preferenceform": document_template,
            "action_name": _("Edit"),
            "title": _("Edit document template"),
        },
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete_set(DocumentTemplate)
def del_document_template(request, instances):
    """View used to delete one or several document templates."""
    document_template = DelDocumentTemplateForm(
        request.POST or None, instances=instances
    )
    if document_template.is_valid():
        document_template_del = document_template.cleaned_data["document_templates"]
        for document_template in document_template_del:
            try:
                document_template.delete()
                messages.success(
                    request,
                    _("The document template %(document_template)s was deleted.")
                    % {"document_template": document_template},
                )
            except ProtectedError:
                messages.error(
                    request,
                    _(
                        "The document template %(document_template)s can't be"
                        " deleted because it is currently being used."
                    )
                    % {"document_template": document_template},
                )
            return redirect(reverse("preferences:display-options"))
    return form(
        {
            "preferenceform": document_template,
            "action_name": _("Delete"),
            "title": _("Delete document template"),
        },
        "preferences/preferences.html",
        request,
    )


@login_required
@can_create(RadiusAttribute)
def add_radiusattribute(request):
    """View used to add RADIUS attributes."""
    attribute = RadiusAttributeForm(request.POST or None)
    if attribute.is_valid():
        attribute.save()
        messages.success(request, _("The attribute was added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": attribute, "action_name": _("Add")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(RadiusAttribute)
def edit_radiusattribute(request, radiusattribute_instance, **_kwargs):
    """View used to edit RADIUS attributes."""
    attribute = RadiusAttributeForm(
        request.POST or None, instance=radiusattribute_instance
    )
    if attribute.is_valid():
        attribute.save()
        messages.success(request, _("The attribute was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": attribute, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(RadiusAttribute)
def del_radiusattribute(request, radiusattribute_instance, **_kwargs):
    """View used to delete RADIUS attributes."""
    if request.method == "POST":
        radiusattribute_instance.delete()
        messages.success(request, _("The attribute was deleted."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"objet": radiusattribute_instance, "objet_name": _("attribute")},
        "preferences/delete.html",
        request,
    )


@login_required
@can_create(Mandate)
def add_mandate(request):
    """View used to add mandates."""
    mandate = MandateForm(request.POST or None)
    if mandate.is_valid():
        mandate.save()
        messages.success(request, _("The mandate was added."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": mandate, "action_name": _("Add")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_edit(Mandate)
def edit_mandate(request, mandate_instance, **_kwargs):
    """View used to edit mandates."""
    mandate = MandateForm(request.POST or None, instance=mandate_instance)
    if mandate.is_valid():
        mandate.save()
        messages.success(request, _("The mandate was edited."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"preferenceform": mandate, "action_name": _("Edit")},
        "preferences/preferences.html",
        request,
    )


@login_required
@can_delete(Mandate)
def del_mandate(request, mandate_instance, **_kwargs):
    """View used to delete mandates."""
    if request.method == "POST":
        mandate_instance.delete()
        messages.success(request, _("The mandate was deleted."))
        return redirect(reverse("preferences:display-options"))
    return form(
        {"objet": mandate_instance, "objet_name": _("mandate")},
        "preferences/delete.html",
        request,
    )
