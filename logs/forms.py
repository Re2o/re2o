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

"""The forms used by the machine search view"""

from django import forms
from django.forms import Form
from django.utils.translation import ugettext_lazy as _
from re2o.base import get_input_formats_help_text

import inspect

# Import all models in which there are classes to be filtered on
import cotisations.models
import machines.models
import preferences.models
import tickets.models
import topologie.models
import users.models


CHOICES_ACTION_TYPE = (
    ("users", _("Users")),
    ("machines", _("Machines")),
    ("subscriptions", _("Subscription")),
    ("whitelists", _("Whitelists")),
    ("bans", _("Bans")),
    ("topology", _("Topology")),
    ("all", _("All")),
)

CHOICES_TYPE = (
    ("ip", _("IPv4")),
    ("mac", _("MAC address")),
)


def all_classes(module):
    classes = []

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            classes.append(name)

    return classes


def classes_for_action_type(action_type):
    """Return the list of class names to be displayed for a
    given actions type filter"""
    if action_type == "users":
        return [
            users.models.User.__name__,
            users.models.Adherent.__name__,
            users.models.Club.__name__,
            users.models.EMailAddress.__name__
        ]

    if action_type == "machines":
        return [
            machines.models.Machine.__name__,
            machines.models.Interface.__name__
        ]

    if action_type == "subscriptions":
        return all_classes(cotisations.models)

    if action_type == "whitelists":
        return [users.models.Whitelist.__name__]

    if action_type == "ban":
        return [users.models.Ban.__name__]

    if action_type == "topology":
        return all_classes(topologie.models)

    # "all" is a special case, just return None
    return None


class ActionsSearchForm(Form):
    """The form for a simple search"""
    u = forms.CharField(
        label=_("Performed by"),
        max_length=100,
        required=False,
    )
    t = forms.MultipleChoiceField(
        label=_("Action type"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=CHOICES_ACTION_TYPE,
        initial=[i[0] for i in CHOICES_ACTION_TYPE],
    )
    s = forms.DateField(required=False, label=_("Start date"))
    e = forms.DateField(required=False, label=_("End date"))

    def __init__(self, *args, **kwargs):
        super(ActionsSearchForm, self).__init__(*args, **kwargs)
        self.fields["s"].help_text = get_input_formats_help_text(
            self.fields["s"].input_formats
        )
        self.fields["e"].help_text = get_input_formats_help_text(
            self.fields["e"].input_formats
        )


class MachineHistorySearchForm(Form):
    """The form for a simple search"""
    q = forms.CharField(
        label=_("Search"),
        max_length=100,
    )
    t = forms.CharField(
        label=_("Search type"),
        widget=forms.Select(choices=CHOICES_TYPE)
    )
    s = forms.DateField(required=False, label=_("Start date"))
    e = forms.DateField(required=False, label=_("End date"))

    def __init__(self, *args, **kwargs):
        super(MachineHistorySearchForm, self).__init__(*args, **kwargs)
        self.fields["s"].help_text = get_input_formats_help_text(
            self.fields["s"].input_formats
        )
        self.fields["e"].help_text = get_input_formats_help_text(
            self.fields["e"].input_formats
        )
