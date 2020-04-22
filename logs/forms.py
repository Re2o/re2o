# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2020  Jean-Romain Garnier
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

from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from re2o.base import get_input_formats_help_text

CHOICES_TYPE = (
    ("ip", _("IPv4")),
    ("mac", _("MAC")),
)


class MachineHistoryForm(Form):
    """The form for a simple search"""

    q = forms.CharField(
        label=_("Search"),
        max_length=100,
    )
    t = forms.CharField(
        label=_("Search type"),
        widget=forms.Select,
        choices=CHOICES_TYPE,
        initial=0,
    )
    s = forms.DateField(required=False, label=_("Start date"))
    e = forms.DateField(required=False, label=_("End date"))

    def __init__(self, *args, **kwargs):
        super(MachineHistoryForm, self).__init__(*args, **kwargs)
        self.fields["s"].help_text = get_input_formats_help_text(
            self.fields["s"].input_formats
        )
        self.fields["e"].help_text = get_input_formats_help_text(
            self.fields["e"].input_formats
        )
