# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020  Gabriel Détraz
# Copyright © 2019  Arthur Grisel-Davy
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

# App de gestion des users pour re2o
# Lara Kermarec, Gabriel Détraz, Lemesle Augustin
# Gplv2

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.forms import modelformset_factory
from re2o.views import form

from re2o.base import re2o_paginator

from re2o.acl import can_view, can_view_all, can_edit, can_create

from preferences.views import edit_options_template_function

from . import forms
from . import models


def aff_preferences(request):
    """ View to display the settings of the tickets in the preferences page"""
    pref, created = models.TicketOption.objects.get_or_create()
    context = {
        "preferences": pref,
        "language": str(pref.LANGUES[pref.mail_language][1]),
    }
    return render_to_string(
        "tickets/preferences.html", context=context, request=request, using=None
    )


@login_required
def edit_options(request, section):
    return edit_options_template_function(request, section, forms, models)
