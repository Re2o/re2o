# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Arthur Grisel-Davy
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
"""
Ticket form
"""


from django import forms
from django.template.loader import render_to_string
from django.forms import ModelForm, Form
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from django.utils.translation import ugettext_lazy as _

from .models import Ticket


class NewTicketForm(FormRevMixin, ModelForm):
    """ Creation of a ticket"""

    class Meta:
        model = Ticket
        fields = ["title", "description", "email"]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super(NewTicketForm, self).__init__(*args, **kwargs)
        if request.user.is_authenticated:
            self.fields.pop('email')
            self.instance.user = request.user
        self.fields['description'].help_text = render_to_string('tickets/help_text.html')
        self.instance.request = request


class EditTicketForm(FormRevMixin, ModelForm):
    """ Creation of a ticket"""

    class Meta:
        model = Ticket
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EditTicketForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False

