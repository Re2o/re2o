# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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
Formulaires d'ajout, edition et suppressions de :
    - machines
    - interfaces
    - domain (noms de machine)
    - alias (cname)
    - service (dhcp, dns..)
    - ns (serveur dns)
    - mx (serveur mail)
    - ports ouverts et profils d'ouverture par interface
"""

from __future__ import unicode_literals

from django.forms import ModelForm, Form
from django import forms

from .models import (
    Domain,
    Machine,
    Interface,
    IpList,
    MachineType,
    Extension,
    Mx,
    Text,
    Ns,
    Service,
    Vlan,
    Nas,
    IpType,
    OuverturePortList,
)


class EditMachineForm(ModelForm):
    """Formulaire d'édition d'une machine"""
    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditMachineForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Nom de la machine'


class NewMachineForm(EditMachineForm):
    """Creation d'une machine, ne renseigne que le nom"""
    class Meta(EditMachineForm.Meta):
        fields = ['name']


class BaseEditMachineForm(EditMachineForm):
    """Edition basique, ne permet que de changer le nom et le statut.
    Réservé aux users sans droits spécifiques"""
    class Meta(EditMachineForm.Meta):
        fields = ['name', 'active']


class EditInterfaceForm(ModelForm):
    """Edition d'une interface. Edition complète"""
    class Meta:
        model = Interface
        fields = ['machine', 'type', 'ipv4', 'mac_address', 'details']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditInterfaceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['mac_address'].label = 'Adresse mac'
        self.fields['type'].label = 'Type de machine'
        self.fields['type'].empty_label = "Séléctionner un type de machine"
        if "ipv4" in self.fields:
            self.fields['ipv4'].empty_label = "Assignation automatique\
            de l'ipv4"
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            )
            # Add it's own address
            self.fields['ipv4'].queryset |= IpList.objects.filter(
                interface=self.instance
            )
        if "machine" in self.fields:
            self.fields['machine'].queryset = Machine.objects.all()\
                .select_related('user')


class AddInterfaceForm(EditInterfaceForm):
    """Ajout d'une interface à une machine. En fonction des droits,
    affiche ou non l'ensemble des ip disponibles"""
    class Meta(EditInterfaceForm.Meta):
        fields = ['type', 'ipv4', 'mac_address', 'details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(AddInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(
                ip_type__in=IpType.objects.filter(need_infra=False)
            )
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            ).filter(ip_type__in=IpType.objects.filter(need_infra=False))
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            )


class NewInterfaceForm(EditInterfaceForm):
    """Formulaire light, sans choix de l'ipv4; d'ajout d'une interface"""
    class Meta(EditInterfaceForm.Meta):
        fields = ['type', 'mac_address', 'details']


class BaseEditInterfaceForm(EditInterfaceForm):
    """Edition basique d'une interface. En fonction des droits,
    ajoute ou non l'ensemble des ipv4 disponibles (infra)"""
    class Meta(EditInterfaceForm.Meta):
        fields = ['type', 'ipv4', 'mac_address', 'details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(BaseEditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(
                ip_type__in=IpType.objects.filter(need_infra=False)
            )
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            ).filter(ip_type__in=IpType.objects.filter(need_infra=False))
            # Add it's own address
            self.fields['ipv4'].queryset |= IpList.objects.filter(
                interface=self.instance
            )
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            )
            self.fields['ipv4'].queryset |= IpList.objects.filter(
                interface=self.instance
            )


class AliasForm(ModelForm):
    """Ajout d'un alias (et edition), CNAME, contenant nom et extension"""
    class Meta:
        model = Domain
        fields = ['name', 'extension']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(AliasForm, self).__init__(*args, prefix=prefix, **kwargs)


class DomainForm(AliasForm):
    """Ajout et edition d'un enregistrement de nom, relié à interface"""
    class Meta(AliasForm.Meta):
        fields = ['name']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
            initial = kwargs.get('initial', {})
            initial['name'] = user.get_next_domain_name()
            kwargs['initial'] = initial
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(DomainForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelAliasForm(Form):
    """Suppression d'un ou plusieurs objets alias"""
    alias = forms.ModelMultipleChoiceField(
        queryset=Domain.objects.all(),
        label="Alias actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        interface = kwargs.pop('interface')
        super(DelAliasForm, self).__init__(*args, **kwargs)
        self.fields['alias'].queryset = Domain.objects.filter(
            cname__in=Domain.objects.filter(interface_parent=interface)
        )


class MachineTypeForm(ModelForm):
    """Ajout et edition d'un machinetype, relié à un iptype"""
    class Meta:
        model = MachineType
        fields = ['type', 'ip_type']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MachineTypeForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['type'].label = 'Type de machine à ajouter'
        self.fields['ip_type'].label = "Type d'ip relié"


class DelMachineTypeForm(Form):
    """Suppression d'un ou plusieurs machinetype"""
    machinetypes = forms.ModelMultipleChoiceField(
        queryset=MachineType.objects.all(),
        label="Types de machines actuelles",
        widget=forms.CheckboxSelectMultiple
    )


class IpTypeForm(ModelForm):
    """Formulaire d'ajout d'un iptype. Pas d'edition de l'ip de start et de
    stop après creation"""
    class Meta:
        model = IpType
        fields = ['type', 'extension', 'need_infra', 'domaine_ip_start',
                  'domaine_ip_stop', 'prefix_v6', 'vlan', 'ouverture_ports']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(IpTypeForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['type'].label = 'Type ip à ajouter'


class EditIpTypeForm(IpTypeForm):
    """Edition d'un iptype. Pas d'edition du rangev4 possible, car il faudrait
    synchroniser les objets iplist"""
    class Meta(IpTypeForm.Meta):
        fields = ['extension', 'type', 'need_infra', 'prefix_v6', 'vlan',
                  'ouverture_ports']


class DelIpTypeForm(Form):
    """Suppression d'un ou plusieurs iptype"""
    iptypes = forms.ModelMultipleChoiceField(
        queryset=IpType.objects.all(),
        label="Types d'ip actuelles",
        widget=forms.CheckboxSelectMultiple
    )


class ExtensionForm(ModelForm):
    """Formulaire d'ajout et edition d'une extension"""
    class Meta:
        model = Extension
        fields = ['name', 'need_infra', 'origin']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ExtensionForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Extension à ajouter'
        self.fields['origin'].label = 'Enregistrement A origin'


class DelExtensionForm(Form):
    """Suppression d'une ou plusieurs extensions"""
    extensions = forms.ModelMultipleChoiceField(
        queryset=Extension.objects.all(),
        label="Extensions actuelles",
        widget=forms.CheckboxSelectMultiple
    )


class MxForm(ModelForm):
    """Ajout et edition d'un MX"""
    class Meta:
        model = Mx
        fields = ['zone', 'priority', 'name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MxForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].queryset = Domain.objects.exclude(
            interface_parent=None
        )


class DelMxForm(Form):
    """Suppression d'un ou plusieurs MX"""
    mx = forms.ModelMultipleChoiceField(
        queryset=Mx.objects.all(),
        label="MX actuels",
        widget=forms.CheckboxSelectMultiple
    )


class NsForm(ModelForm):
    """Ajout d'un NS pour une zone"""
    class Meta:
        model = Ns
        fields = ['zone', 'ns']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NsForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['ns'].queryset = Domain.objects.exclude(
            interface_parent=None
        )


class DelNsForm(Form):
    """Suppresion d'un ou plusieurs NS"""
    ns = forms.ModelMultipleChoiceField(
        queryset=Ns.objects.all(),
        label="Enregistrements NS actuels",
        widget=forms.CheckboxSelectMultiple
    )


class TxtForm(ModelForm):
    """Ajout d'un txt pour une zone"""
    class Meta:
        model = Text
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(TxtForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelTxtForm(Form):
    """Suppression d'un ou plusieurs TXT"""
    txt = forms.ModelMultipleChoiceField(
        queryset=Text.objects.all(),
        label="Enregistrements Txt actuels",
        widget=forms.CheckboxSelectMultiple
    )


class NasForm(ModelForm):
    """Ajout d'un type de nas (machine d'authentification,
    swicths, bornes...)"""
    class Meta:
        model = Nas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NasForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelNasForm(Form):
    """Suppression d'un ou plusieurs nas"""
    nas = forms.ModelMultipleChoiceField(
        queryset=Nas.objects.all(),
        label="Enregistrements Nas actuels",
        widget=forms.CheckboxSelectMultiple
    )


class ServiceForm(ModelForm):
    """Ajout et edition d'une classe de service : dns, dhcp, etc"""
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['servers'].queryset = Interface.objects.all()\
        .select_related('domain__extension')

    def save(self, commit=True):
        instance = super(ServiceForm, self).save(commit=False)
        if commit:
            instance.save()
        instance.process_link(self.cleaned_data.get('servers'))
        return instance


class DelServiceForm(Form):
    """Suppression d'un ou plusieurs service"""
    service = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        label="Services actuels",
        widget=forms.CheckboxSelectMultiple
    )


class VlanForm(ModelForm):
    """Ajout d'un vlan : id, nom"""
    class Meta:
        model = Vlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(VlanForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelVlanForm(Form):
    """Suppression d'un ou plusieurs vlans"""
    vlan = forms.ModelMultipleChoiceField(
        queryset=Vlan.objects.all(),
        label="Vlan actuels",
        widget=forms.CheckboxSelectMultiple
    )


class EditOuverturePortConfigForm(ModelForm):
    """Edition de la liste des profils d'ouverture de ports
    pour l'interface"""
    class Meta:
        model = Interface
        fields = ['port_lists']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOuverturePortConfigForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )


class EditOuverturePortListForm(ModelForm):
    """Edition de la liste des ports et profils d'ouverture
    des ports"""
    class Meta:
        model = OuverturePortList
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOuverturePortListForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
