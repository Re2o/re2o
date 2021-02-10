# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Gabriel Détraz
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
The database models for the 'preference' app of re2o.

For further details on each of those models, see the documentation details for
each.
"""


from django import forms
from django.forms import Form, ModelForm
from django.utils.translation import ugettext_lazy as _

from re2o.widgets import AutocompleteMultipleModelWidget

from .models import MultiopOption


class EditMultiopOptionForm(ModelForm):
    """Form used to edit the settings of multi_op."""

    class Meta:
        model = MultiopOption
        fields = "__all__"
        widgets = {
            "enabled_dorm": AutocompleteMultipleModelWidget(
                url="/topologie/dormitory-autocomplete",
            ),
        }
