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

from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import Domain, Machine, Interface, IpList, MachineType, Extension, Mx, Text, Ns, Service, Vlan, Nas, IpType
from django.db.models import Q
from django.core.validators import validate_email

from users.models import User

class EditMachineForm(ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditMachineForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom de la machine'

class NewMachineForm(EditMachineForm):
    class Meta(EditMachineForm.Meta):
        fields = ['name']

class BaseEditMachineForm(EditMachineForm):
    class Meta(EditMachineForm.Meta):
        fields = ['name','active']

class EditInterfaceForm(ModelForm):
    class Meta:
        model = Interface
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['mac_address'].label = 'Adresse mac'
        self.fields['type'].label = 'Type de machine'
        self.fields['type'].empty_label = "Séléctionner un type de machine"
        if "ipv4" in self.fields:
            self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True)
        if "machine" in self.fields:
            self.fields['machine'].queryset = Machine.objects.all().select_related('user')

class AddInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['type','ipv4','mac_address','details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(AddInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(ip_type__in=IpType.objects.filter(need_infra=False))
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True).filter(ip_type__in=IpType.objects.filter(need_infra=False))
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True)

class NewInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['mac_address','type','details']

class BaseEditInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','type','details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(BaseEditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(ip_type__in=IpType.objects.filter(need_infra=False))
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True).filter(ip_type__in=IpType.objects.filter(need_infra=False))
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True)

class AliasForm(ModelForm):
    class Meta:
        model = Domain
        fields = ['name','extension']

    def __init__(self, *args, **kwargs):
        if 'infra' in kwargs:
            infra = kwargs.pop('infra')
        super(AliasForm, self).__init__(*args, **kwargs)

class DomainForm(AliasForm):
    class Meta(AliasForm.Meta):
        fields = ['name']

    def __init__(self, *args, **kwargs):
        if 'name_user' in kwargs:
            name_user = kwargs.pop('name_user')
            nb_machine = kwargs.pop('nb_machine')
            initial = kwargs.get('initial', {})
            initial['name'] = name_user.lower()+str(nb_machine)
            kwargs['initial'] = initial 
        super(DomainForm, self).__init__(*args, **kwargs)
 
class DelAliasForm(Form):
    alias = forms.ModelMultipleChoiceField(queryset=Domain.objects.all(), label="Alias actuels",  widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        interface = kwargs.pop('interface')
        super(DelAliasForm, self).__init__(*args, **kwargs)
        self.fields['alias'].queryset = Domain.objects.filter(cname__in=Domain.objects.filter(interface_parent=interface))

class MachineTypeForm(ModelForm):
    class Meta:
        model = MachineType
        fields = ['type','ip_type']

    def __init__(self, *args, **kwargs):
        super(MachineTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type de machine à ajouter'
        self.fields['ip_type'].label = "Type d'ip relié"

class DelMachineTypeForm(Form):
    machinetypes = forms.ModelMultipleChoiceField(queryset=MachineType.objects.all(), label="Types de machines actuelles",  widget=forms.CheckboxSelectMultiple)

class IpTypeForm(ModelForm):
    class Meta:
        model = IpType
        fields = ['type','extension','need_infra','domaine_ip_start','domaine_ip_stop', 'vlan']
        

    def __init__(self, *args, **kwargs):
        super(IpTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type ip à ajouter'

class EditIpTypeForm(IpTypeForm):
    class Meta(IpTypeForm.Meta):
        fields = ['extension','type','need_infra', 'vlan']

class DelIpTypeForm(Form):
    iptypes = forms.ModelMultipleChoiceField(queryset=IpType.objects.all(), label="Types d'ip actuelles",  widget=forms.CheckboxSelectMultiple)

class ExtensionForm(ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'need_infra', 'origin']

    def __init__(self, *args, **kwargs):
        super(ExtensionForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Extension à ajouter'
        self.fields['origin'].label = 'Enregistrement A origin'

class DelExtensionForm(Form):
    extensions = forms.ModelMultipleChoiceField(queryset=Extension.objects.all(), label="Extensions actuelles",  widget=forms.CheckboxSelectMultiple)

class MxForm(ModelForm):
    class Meta:
        model = Mx
        fields = ['zone', 'priority', 'name']
      
    def __init__(self, *args, **kwargs):
        super(MxForm, self).__init__(*args, **kwargs)
        self.fields['name'].queryset = Domain.objects.exclude(interface_parent=None)
  
class DelMxForm(Form):
    mx = forms.ModelMultipleChoiceField(queryset=Mx.objects.all(), label="MX actuels",  widget=forms.CheckboxSelectMultiple)

class NsForm(ModelForm):
    class Meta:
        model = Ns
        fields = ['zone', 'ns']

    def __init__(self, *args, **kwargs):
        super(NsForm, self).__init__(*args, **kwargs)
        self.fields['ns'].queryset = Domain.objects.exclude(interface_parent=None)

class DelNsForm(Form):
    ns = forms.ModelMultipleChoiceField(queryset=Ns.objects.all(), label="Enregistrements NS actuels",  widget=forms.CheckboxSelectMultiple)

class TextForm(ModelForm):
    class Meta:
        model = Text
        fields = '__all__'

class DelTextForm(Form):
    text = forms.ModelMultipleChoiceField(queryset=Text.objects.all(), label="Enregistrements Text actuels",  widget=forms.CheckboxSelectMultiple)

class NasForm(ModelForm):
    class Meta:
        model = Nas
        fields = '__all__'

class DelNasForm(Form):
    nas = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), label="Enregistrements Nas actuels",  widget=forms.CheckboxSelectMultiple)

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

    def save(self, commit=True):
        instance = super(ServiceForm, self).save(commit=False)
        if commit:
            instance.save()
        instance.process_link(self.cleaned_data.get('servers'))
        return instance

class DelServiceForm(Form):
    service = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), label="Services actuels",  widget=forms.CheckboxSelectMultiple)

class VlanForm(ModelForm):
    class Meta:
        model = Vlan
        fields = '__all__'

class DelVlanForm(Form):
    vlan = forms.ModelMultipleChoiceField(queryset=Vlan.objects.all(), label="Vlan actuels",  widget=forms.CheckboxSelectMultiple)



