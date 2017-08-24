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

from .models import OptionalUser, OptionalMachine, AssoOption, GeneralOption 
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
    generaloptions, created = GeneralOption.objects.get_or_create()
    assooptions, crated = AssoOption.objects.get_or_create()
    return form({'useroptions': useroptions, 'machineoptions': machineoptions, 'generaloptions': generaloptions, 'assooptions' : assooptions}, 'preferences/display_preferences.html', request)

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

