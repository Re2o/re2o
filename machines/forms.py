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

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin

from .models import (
    Domain,
    Machine,
    Interface,
    IpList,
    MachineType,
    Extension,
    SOA,
    Mx,
    Txt,
    Ns,
    Service,
    Vlan,
    Srv,
    Nas,
    IpType,
    OuverturePortList,
    Ipv6List,
    SshFingerprint,
    SshFprAlgo
)


class EditMachineForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
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


class EditInterfaceForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Edition d'une interface. Edition complète"""
    class Meta:
        model = Interface
        fields = ['machine', 'type', 'ipv4', 'mac_address', 'details']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        user = kwargs.get('user')
        super(EditInterfaceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['mac_address'].label = 'Adresse mac'
        self.fields['type'].label = 'Type de machine'
        self.fields['type'].empty_label = "Séléctionner un type de machine"
        if "ipv4" in self.fields:
            self.fields['ipv4'].empty_label = ("Assignation automatique de "
                                               "l'ipv4")
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            )
            can_use_all_iptype, _reason = IpType.can_use_all(user)
            if not can_use_all_iptype:
                self.fields['ipv4'].queryset = IpList.objects.filter(
                    interface__isnull=True
                ).filter(ip_type__in=IpType.objects.filter(need_infra=False))
            else:
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
        can_use_all_machinetype, _reason = MachineType.can_use_all(user)
        if not can_use_all_machinetype:
            self.fields['type'].queryset = MachineType.objects.filter(
                ip_type__in=IpType.objects.filter(need_infra=False)
            )


class AddInterfaceForm(EditInterfaceForm):
    """Ajout d'une interface à une machine. En fonction des droits,
    affiche ou non l'ensemble des ip disponibles"""
    class Meta(EditInterfaceForm.Meta):
        fields = ['type', 'ipv4', 'mac_address', 'details']


class AliasForm(FormRevMixin, ModelForm):
    """Ajout d'un alias (et edition), CNAME, contenant nom et extension"""
    class Meta:
        model = Domain
        fields = ['name', 'extension']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        user = kwargs.pop('user')
        super(AliasForm, self).__init__(*args, prefix=prefix, **kwargs)
        can_use_all, _reason = Extension.can_use_all(user)
        if not can_use_all:
            self.fields['extension'].queryset = Extension.objects.filter(
                need_infra=False
            )


class DomainForm(FormRevMixin, ModelForm):
    """Ajout et edition d'un enregistrement de nom, relié à interface"""
    class Meta:
        model = Domain
        fields = ['name']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
            initial = kwargs.get('initial', {})
            initial['name'] = user.get_next_domain_name()
            kwargs['initial'] = initial
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(DomainForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelAliasForm(FormRevMixin, Form):
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


class MachineTypeForm(FormRevMixin, ModelForm):
    """Ajout et edition d'un machinetype, relié à un iptype"""
    class Meta:
        model = MachineType
        fields = ['type', 'ip_type']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MachineTypeForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['type'].label = 'Type de machine à ajouter'
        self.fields['ip_type'].label = "Type d'ip relié"


class DelMachineTypeForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs machinetype"""
    machinetypes = forms.ModelMultipleChoiceField(
        queryset=MachineType.objects.none(),
        label="Types de machines actuelles",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelMachineTypeForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['machinetypes'].queryset = instances
        else:
            self.fields['machinetypes'].queryset = MachineType.objects.all()


class IpTypeForm(FormRevMixin, ModelForm):
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


class DelIpTypeForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs iptype"""
    iptypes = forms.ModelMultipleChoiceField(
        queryset=IpType.objects.none(),
        label="Types d'ip actuelles",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelIpTypeForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['iptypes'].queryset = instances
        else:
            self.fields['iptypes'].queryset = IpType.objects.all()


class ExtensionForm(FormRevMixin, ModelForm):
    """Formulaire d'ajout et edition d'une extension"""
    class Meta:
        model = Extension
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ExtensionForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Extension à ajouter'
        self.fields['origin'].label = 'Enregistrement A origin'
        self.fields['origin_v6'].label = 'Enregistrement AAAA origin'
        self.fields['soa'].label = 'En-tête SOA à utiliser'


class DelExtensionForm(FormRevMixin, Form):
    """Suppression d'une ou plusieurs extensions"""
    extensions = forms.ModelMultipleChoiceField(
        queryset=Extension.objects.none(),
        label="Extensions actuelles",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelExtensionForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['extensions'].queryset = instances
        else:
            self.fields['extensions'].queryset = Extension.objects.all()


class Ipv6ListForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Gestion des ipv6 d'une machine"""
    class Meta:
        model = Ipv6List
        fields = ['ipv6', 'slaac_ip']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(Ipv6ListForm, self).__init__(*args, prefix=prefix, **kwargs)


class SOAForm(FormRevMixin, ModelForm):
    """Ajout et edition d'un SOA"""
    class Meta:
        model = SOA
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SOAForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelSOAForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs SOA"""
    soa = forms.ModelMultipleChoiceField(
        queryset=SOA.objects.none(),
        label="SOA actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelSOAForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['soa'].queryset = instances
        else:
            self.fields['soa'].queryset = SOA.objects.all()


class MxForm(FormRevMixin, ModelForm):
    """Ajout et edition d'un MX"""
    class Meta:
        model = Mx
        fields = ['zone', 'priority', 'name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MxForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].queryset = Domain.objects.exclude(
            interface_parent=None
        ).select_related('extension')


class DelMxForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs MX"""
    mx = forms.ModelMultipleChoiceField(
        queryset=Mx.objects.none(),
        label="MX actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelMxForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['mx'].queryset = instances
        else:
            self.fields['mx'].queryset = Mx.objects.all()


class NsForm(FormRevMixin, ModelForm):
    """Ajout d'un NS pour une zone
    On exclue les CNAME dans les objets domain (interdit par la rfc)
    donc on prend uniquemet """
    class Meta:
        model = Ns
        fields = ['zone', 'ns']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NsForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['ns'].queryset = Domain.objects.exclude(
            interface_parent=None
        ).select_related('extension')


class DelNsForm(FormRevMixin, Form):
    """Suppresion d'un ou plusieurs NS"""
    ns = forms.ModelMultipleChoiceField(
        queryset=Ns.objects.none(),
        label="Enregistrements NS actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelNsForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['ns'].queryset = instances
        else:
            self.fields['ns'].queryset = Ns.objects.all()


class TxtForm(FormRevMixin, ModelForm):
    """Ajout d'un txt pour une zone"""
    class Meta:
        model = Txt
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(TxtForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelTxtForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs TXT"""
    txt = forms.ModelMultipleChoiceField(
        queryset=Txt.objects.none(),
        label="Enregistrements Txt actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelTxtForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['txt'].queryset = instances
        else:
            self.fields['txt'].queryset = Txt.objects.all()


class SrvForm(FormRevMixin, ModelForm):
    """Ajout d'un srv pour une zone"""
    class Meta:
        model = Srv
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SrvForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelSrvForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs Srv"""
    srv = forms.ModelMultipleChoiceField(
        queryset=Srv.objects.none(),
        label="Enregistrements Srv actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelSrvForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['srv'].queryset = instances
        else:
            self.fields['srv'].queryset = Srv.objects.all()


class NasForm(FormRevMixin, ModelForm):
    """Ajout d'un type de nas (machine d'authentification,
    swicths, bornes...)"""
    class Meta:
        model = Nas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NasForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelNasForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs nas"""
    nas = forms.ModelMultipleChoiceField(
        queryset=Nas.objects.none(),
        label="Enregistrements Nas actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelNasForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['nas'].queryset = instances
        else:
            self.fields['nas'].queryset = Nas.objects.all()


class ServiceForm(FormRevMixin, ModelForm):
    """Ajout et edition d'une classe de service : dns, dhcp, etc"""
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['servers'].queryset = (Interface.objects.all()
                                           .select_related(
                                               'domain__extension'
                                           ))

    def save(self, commit=True):
        # TODO : None of the parents of ServiceForm use the commit
        # parameter in .save()
        instance = super(ServiceForm, self).save(commit=False)
        if commit:
            instance.save()
        instance.process_link(self.cleaned_data.get('servers'))
        return instance


class DelServiceForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs service"""
    service = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label="Services actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['service'].queryset = instances
        else:
            self.fields['service'].queryset = Service.objects.all()


class VlanForm(FormRevMixin, ModelForm):
    """Ajout d'un vlan : id, nom"""
    class Meta:
        model = Vlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(VlanForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelVlanForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs vlans"""
    vlan = forms.ModelMultipleChoiceField(
        queryset=Vlan.objects.none(),
        label="Vlan actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelVlanForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['vlan'].queryset = instances
        else:
            self.fields['vlan'].queryset = Vlan.objects.all()


class EditOuverturePortConfigForm(FormRevMixin, ModelForm):
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


class EditOuverturePortListForm(FormRevMixin, ModelForm):
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

        
class SshFingerprintForm(FormRevMixin, ModelForm):
    """Edition d'une sshfingerprint"""
    class Meta:
        model = SshFingerprint
        exclude = ('machine',)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SshFingerprintForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )


class SshFprAlgoForm(FormRevMixin, ModelForm):
    """Edition de la liste des algo pour sshfpr"""
    class Meta:
        model = SshFprAlgo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SshFprAlgoForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
