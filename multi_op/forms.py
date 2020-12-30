# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Maël Kervella
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
Select a dorm
"""


from django import forms
from django.forms import ModelForm, Form
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from django.utils.translation import ugettext_lazy as _

from topologie.models import Dormitory

from .preferences.models import MultiopOption


class DormitoryForm(FormRevMixin, Form):
    """Form used to select dormitories."""

    dormitory = forms.ModelMultipleChoiceField(
        label=_("Dormitory"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        queryset=Dormitory.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super(DormitoryForm, self).__init__(*args, **kwargs)
        self.fields["dormitory"].queryset = MultiopOption.get_cached_value("enabled_dorm").all()
