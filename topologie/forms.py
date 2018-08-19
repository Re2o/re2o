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
"""
Un forms le plus simple possible pour les objets topologie de re2o.

Permet de créer et supprimer : un Port de switch, relié à un switch.

Permet de créer des stacks et d'y ajouter des switchs (StackForm)

Permet de créer, supprimer et editer un switch (EditSwitchForm,
NewSwitchForm)
"""

from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _

from machines.models import Interface
from machines.forms import (
    EditMachineForm,
    NewMachineForm
)
from re2o.mixins import FormRevMixin

from .models import (
    Port,
    Switch,
    Room,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint,
    SwitchBay,
    Building,
    PortProfile,
)


class PortForm(FormRevMixin, ModelForm):
    """Formulaire pour la création d'un port d'un switch
    Relié directement au modèle port"""
    class Meta:
        model = Port
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PortForm, self).__init__(*args, prefix=prefix, **kwargs)


class EditPortForm(FormRevMixin, ModelForm):
    """Form pour l'édition d'un port de switche : changement des reglages
    radius ou vlan, ou attribution d'une chambre, autre port ou machine

    Un port est relié à une chambre, un autre port (uplink) ou une machine
    (serveur ou borne), mutuellement exclusif
    Optimisation sur les queryset pour machines et port_related pour
    optimiser le temps de chargement avec select_related (vraiment
    lent sans)"""
    class Meta(PortForm.Meta):
        fields = ['room', 'related', 'machine_interface', 'custom_profile',
                  'state', 'details']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditPortForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['machine_interface'].queryset = (
            Interface.objects.all().select_related('domain__extension')
        )
        self.fields['related'].queryset = Port.objects.all().prefetch_related('switch__machine_ptr__interface_set__domain__extension')


class AddPortForm(FormRevMixin, ModelForm):
    """Permet d'ajouter un port de switch. Voir EditPortForm pour plus
    d'informations"""
    class Meta(PortForm.Meta):
        fields = [
            'port',
            'room',
            'machine_interface',
            'related',
            'custom_profile',
            'state',
            'details'
        ]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(AddPortForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['machine_interface'].queryset = (
            Interface.objects.all().select_related('domain__extension')
        )
        self.fields['related'].queryset = (
            Port.objects.all().prefetch_related(Prefetch(
                'switch__interface_set',
                queryset=(Interface.objects
                          .select_related('ipv4__ip_type__extension')
                          .select_related('domain__extension'))
            ))
        )


class StackForm(FormRevMixin, ModelForm):
    """Permet d'edition d'une stack : stack_id, et switches membres
    de la stack"""
    class Meta:
        model = Stack
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(StackForm, self).__init__(*args, prefix=prefix, **kwargs)


class AddAccessPointForm(NewMachineForm):
    """Formulaire pour la création d'une borne
    Relié directement au modèle borne"""
    class Meta:
        model = AccessPoint
        fields = ['location', 'name']


class EditAccessPointForm(EditMachineForm):
    """Edition d'une borne. Edition complète"""
    class Meta:
        model = AccessPoint
        fields = '__all__'


class EditSwitchForm(EditMachineForm):
    """Permet d'éditer un switch : nom et nombre de ports"""
    class Meta:
        model = Switch
        fields = '__all__'


class NewSwitchForm(NewMachineForm):
    """Permet de créer un switch : emplacement, paramètres machine,
    membre d'un stack (option), nombre de ports (number)"""
    class Meta(EditSwitchForm.Meta):
        fields = ['name', 'switchbay', 'number', 'stack', 'stack_member_id']


class EditRoomForm(FormRevMixin, ModelForm):
    """Permet d'éediter le nom et commentaire d'une prise murale"""
    class Meta:
        model = Room
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditRoomForm, self).__init__(*args, prefix=prefix, **kwargs)


class CreatePortsForm(forms.Form):
    """Permet de créer une liste de ports pour un switch."""
    begin = forms.IntegerField(label=_("Start:"), min_value=0)
    end = forms.IntegerField(label=_("End:"), min_value=0)


class EditModelSwitchForm(FormRevMixin, ModelForm):
    """Permet d'éediter un modèle de switch : nom et constructeur"""
    members = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        required=False
    )

    class Meta:
        model = ModelSwitch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditModelSwitchForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['members'] = Switch.objects.filter(model=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set = self.cleaned_data['members']
        return instance


class EditConstructorSwitchForm(FormRevMixin, ModelForm):
    """Permet d'éediter le nom d'un constructeur"""
    class Meta:
        model = ConstructorSwitch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditConstructorSwitchForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )


class EditSwitchBayForm(FormRevMixin, ModelForm):
    """Permet d'éditer une baie de brassage"""
    members = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        required=False
    )

    class Meta:
        model = SwitchBay
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditSwitchBayForm, self).__init__(*args, prefix=prefix, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['members'] = Switch.objects.filter(switchbay=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set = self.cleaned_data['members']
        return instance


class EditBuildingForm(FormRevMixin, ModelForm):
    """Permet d'éditer le batiment"""
    class Meta:
        model = Building
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditBuildingForm, self).__init__(*args, prefix=prefix, **kwargs)

class EditPortProfileForm(FormRevMixin, ModelForm):
    """Form to edit a port profile"""
    class Meta:
        model = PortProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditPortProfileForm, self).__init__(*args,
                                                  prefix=prefix,
                                                  **kwargs)

