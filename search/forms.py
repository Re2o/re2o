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

"""The forms used by the search app"""

from __future__ import unicode_literals

from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from re2o.base import get_input_formats_help_text

CHOICES_USER = (
    ("0", _("Active")),
    ("1", _("Disabled")),
    ("2", _("Archived")),
    ("3", _("Not yet active")),
    ("4", _("Fully archived")),
    ("5", _("Waiting for email confirmation")),
    ("6", _("Suspended")),
)

CHOICES_AFF = (
    ("0", _("Users")),
    ("1", _("Machines")),
    ("2", _("Invoices")),
    ("3", _("Bans")),
    ("4", _("Whitelists")),
    ("5", _("Rooms")),
    ("6", _("Ports")),
    ("7", _("Switches")),
)


def initial_choices(choice_set):
    """Return the choices that should be activated by default for a
    given set of choices"""
    return [i[0] for i in choice_set]


class SearchForm(Form):
    """The form for a simple search"""

    q = forms.CharField(
        label=_("Search"),
        help_text=(
            _(
                'Use « » and «,» to specify distinct words, «"query"» for'
                " an exact search, «\\» to escape a character and «+» to"
                " combine keywords."
            )
        ),
        max_length=100,
    )


class SearchFormPlus(Form):
    """The form for an advanced search (with filters)"""

    q = forms.CharField(
        label=_("Search"),
        help_text=(
            _(
                'Use « » and «,» to specify distinct words, «"query"» for'
                " an exact search, «\\» to escape a character and «+» to"
                " combine keywords."
            )
        ),
        max_length=100,
        required=False,
    )
    u = forms.MultipleChoiceField(
        label=_("Users filter"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES_USER,
        initial=initial_choices(CHOICES_USER),
    )
    a = forms.MultipleChoiceField(
        label=_("Display filter"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES_AFF,
        initial=initial_choices(CHOICES_AFF),
    )
    s = forms.DateField(required=False, label=_("Start date"))
    e = forms.DateField(required=False, label=_("End date"))

    def __init__(self, *args, **kwargs):
        super(SearchFormPlus, self).__init__(*args, **kwargs)
        self.fields["s"].help_text = get_input_formats_help_text(
            self.fields["s"].input_formats
        )
        self.fields["e"].help_text = get_input_formats_help_text(
            self.fields["e"].input_formats
        )
