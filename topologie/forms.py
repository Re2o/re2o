# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
"""
Forms for the topologie app of re2o.

The forms are used to:
    * create and delete switch ports, related to a switch.
    * create stacks and add switches to them (StackForm).
    * create, edit and delete a switch (NewSwitchForm, EditSwitchForm).
"""

from __future__ import unicode_literals

from django import forms
from django.db.models import Prefetch
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from machines.forms import EditMachineForm, NewMachineForm
from machines.models import Interface
from re2o.mixins import FormRevMixin
from re2o.widgets import (AutocompleteModelWidget,
                          AutocompleteMultipleModelWidget)

from .models import (AccessPoint, Building, ConstructorSwitch, Dormitory,
                     ModelSwitch, ModuleOnSwitch, ModuleSwitch, Port,
                     PortProfile, Room, Stack, Switch, SwitchBay)


class PortForm(FormRevMixin, ModelForm):
    """Form used to manage a switch's port."""

    class Meta:
        model = Port
        fields = "__all__"
        widgets = {
            "switch": AutocompleteModelWidget(url="/topologie/switch-autocomplete"),
            "room": AutocompleteModelWidget(url="/topologie/room-autocomplete"),
            "machine_interface": AutocompleteModelWidget(
                url="/machines/interface-autocomplete"
            ),
            "related": AutocompleteModelWidget(url="/topologie/port-autocomplete"),
            "custom_profile": AutocompleteModelWidget(
                url="/topologie/portprofile-autocomplete"
            ),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(PortForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditPortForm(FormRevMixin, ModelForm):
    """Form used to edit a switch's port: change in RADIUS or VLANs settings,
    assignement to a room, port or machine.

    A port is related to either a room, another port (uplink) or a machine (server or AP).
    """

    class Meta(PortForm.Meta):
        fields = [
            "room",
            "related",
            "machine_interface",
            "custom_profile",
            "state",
            "details",
        ]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditPortForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields[
            "machine_interface"
        ].queryset = Interface.objects.all().select_related("domain__extension")
        self.fields["related"].queryset = Port.objects.all().prefetch_related(
            "switch__machine_ptr__interface_set__domain__extension"
        )
        self.fields["room"].queryset = Room.objects.all().select_related(
            "building__dormitory"
        )


class AddPortForm(FormRevMixin, ModelForm):
    """Form used to add a switch's port. See EditPortForm."""

    class Meta(PortForm.Meta):
        fields = [
            "port",
            "room",
            "machine_interface",
            "related",
            "custom_profile",
            "state",
            "details",
        ]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(AddPortForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields[
            "machine_interface"
        ].queryset = Interface.objects.all().select_related("domain__extension")
        self.fields["related"].queryset = Port.objects.all().prefetch_related(
            Prefetch(
                "switch__interface_set",
                queryset=(
                    Interface.objects.select_related(
                        "ipv4__ip_type__extension"
                    ).select_related("domain__extension")
                ),
            )
        )


class StackForm(FormRevMixin, ModelForm):
    """Form used to create and edit stacks."""

    class Meta:
        model = Stack
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(StackForm, self).__init__(*args, prefix=prefix, **kwargs)


class AddAccessPointForm(NewMachineForm):
    """Form used to create access points."""

    class Meta:
        model = AccessPoint
        fields = ["location", "name"]


class EditAccessPointForm(EditMachineForm):
    """Form used to edit access points."""

    class Meta(EditMachineForm.Meta):
        model = AccessPoint
        fields = "__all__"


class EditSwitchForm(EditMachineForm):
    """Form used to edit switches."""

    class Meta(EditMachineForm.Meta):
        model = Switch
        fields = "__all__"
        widgets = {
            "switchbay": AutocompleteModelWidget(
                url="/topologie/switchbay-autocomplete"
            ),
            "user": AutocompleteModelWidget(url="/users/user-autocomplete"),
        }


class NewSwitchForm(NewMachineForm):
    """Form used to create a switch."""

    class Meta(EditSwitchForm.Meta):
        fields = ["name", "switchbay", "number", "stack", "stack_member_id"]


class EditRoomForm(FormRevMixin, ModelForm):
    """Form used to edit a room."""

    class Meta:
        model = Room
        fields = "__all__"
        widgets = {
            "building": AutocompleteModelWidget(url="/topologie/building-autocomplete")
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditRoomForm, self).__init__(*args, prefix=prefix, **kwargs)


class CreatePortsForm(forms.Form):
    """Form used to create switch ports lists."""

    begin = forms.IntegerField(label=_("Start:"), min_value=0)
    end = forms.IntegerField(label=_("End:"), min_value=0)


class EditModelSwitchForm(FormRevMixin, ModelForm):
    """Form used to edit switch models."""

    members = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        widget=AutocompleteMultipleModelWidget(url="/topologie/switch-autocomplete"),
        required=False,
    )

    class Meta:
        model = ModelSwitch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditModelSwitchForm, self).__init__(*args, prefix=prefix, **kwargs)
        instance = kwargs.get("instance", None)
        if instance:
            self.initial["members"] = Switch.objects.filter(model=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set.set(self.cleaned_data["members"])
        return instance


class EditConstructorSwitchForm(FormRevMixin, ModelForm):
    """Form used to edit switch constructors."""

    class Meta:
        model = ConstructorSwitch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditConstructorSwitchForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditSwitchBayForm(FormRevMixin, ModelForm):
    """Form used to edit switch bays."""

    members = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        required=False,
        widget=AutocompleteMultipleModelWidget(url="/topologie/switch-autocomplete"),
    )

    class Meta:
        model = SwitchBay
        fields = "__all__"
        widgets = {
            "building": AutocompleteModelWidget(url="/topologie/building-autocomplete")
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditSwitchBayForm, self).__init__(*args, prefix=prefix, **kwargs)
        instance = kwargs.get("instance", None)
        if instance:
            self.initial["members"] = Switch.objects.filter(switchbay=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set.set(self.cleaned_data["members"])
        return instance


class EditBuildingForm(FormRevMixin, ModelForm):
    """Form used to edit buildings."""

    class Meta:
        model = Building
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditBuildingForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditDormitoryForm(FormRevMixin, ModelForm):
    """Form used to edit dormitories."""

    class Meta:
        model = Dormitory
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditDormitoryForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditPortProfileForm(FormRevMixin, ModelForm):
    """Form used to edit port profiles."""

    class Meta:
        model = PortProfile
        fields = "__all__"
        widgets = {
            "vlan_tagged": AutocompleteMultipleModelWidget(
                url="/machines/vlan-autocomplete"
            ),
            "vlan_untagged": AutocompleteModelWidget(url="/machines/vlan-autocomplete"),
        }

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditPortProfileForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditModuleForm(FormRevMixin, ModelForm):
    """Form used to add and edit switch modules."""

    class Meta:
        model = ModuleSwitch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditModuleForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditSwitchModuleForm(FormRevMixin, ModelForm):
    """Form used to add and edit modules related to a switch."""

    class Meta:
        model = ModuleOnSwitch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(EditSwitchModuleForm, self).__init__(*args, prefix=prefix, **kwargs)
