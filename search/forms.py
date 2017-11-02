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

from __future__ import unicode_literals

from django import forms
from django.forms import Form

CHOICES_USER = (
    ('0', 'Actifs'),
    ('1', 'Désactivés'),
    ('2', 'Archivés'),
)

CHOICES_AFF = (
    ('0', 'Utilisateurs'),
    ('1', 'Machines'),
    ('2', 'Factures'),
    ('3', 'Bannissements'),
    ('4', 'Accès à titre gracieux'),
    ('6', 'Switchs'),
    ('5', 'Ports'),
)


def initial_choices(c):
    return [i[0] for i in c]


class SearchForm(Form):
    q = forms.CharField(label='Search', max_length=100)


class SearchFormPlus(Form):
    q = forms.CharField(
        label='Search',
        max_length=100,
        required=False
    )
    u = forms.MultipleChoiceField(
        label="Filtre utilisateurs",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES_USER,
        initial=initial_choices(CHOICES_USER)
    )
    a = forms.MultipleChoiceField(
        label="Filtre affichage",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES_AFF,
        initial=initial_choices(CHOICES_AFF)
    )
    s = forms.DateField(
        required=False,
        label="Date de début",
        help_text='DD/MM/YYYY',
        input_formats=['%d/%m/%Y']
    )
    e = forms.DateField(
        required=False,
        help_text='DD/MM/YYYY',
        input_formats=['%d/%m/%Y'],
        label="Date de fin"
    )
