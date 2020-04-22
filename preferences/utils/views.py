# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020  Gabriel Détraz
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
Utils for preferences
"""

from __future__ import unicode_literals
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import ProtectedError
from django.db import transaction
from django.utils.translation import ugettext as _

from reversion import revisions as reversion

from re2o.views import form

def edit_options_template_function(request, section, forms, models):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, "Edit" + section + "Form", None)
    if not (model or form_instance):
        messages.error(request, _("Unknown object."))
        return redirect(reverse("preferences:display-options"))

    options_instance, _created = model.objects.get_or_create()
    can, msg, permissions = options_instance.can_edit(request.user)
    if not can:
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


