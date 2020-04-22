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
Ticket preferences form
"""

from django import forms
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _

from re2o.mixins import FormRevMixin
from .models import TicketOption


class EditTicketOptionForm(FormRevMixin, ModelForm):
    """ Edit the ticket's settings"""

    class Meta:
        model = TicketOption
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditTicketOptionForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["publish_address"].label = _("Publish address")
        self.fields["mail_language"].label = _("Mail language")
