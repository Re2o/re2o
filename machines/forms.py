from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import Alias, Machine, Interface, IpList, MachineType, Extension, Mx, Ns, IpType
from django.db.models import Q

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
        self.fields['dns'].label = 'Nom dns de la machine'
        self.fields['mac_address'].label = 'Adresse mac'
        self.fields['type'].label = 'Type de machine'
        self.fields['type'].empty_label = "Séléctionner un type de machine"

class AddInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','dns','type','details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(AddInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(ip_type=IpType.objects.filter(need_infra=False))
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True).filter(ip_type=IpType.objects.filter(need_infra=False)).filter(need_infra=False)
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True)

class NewInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['mac_address','dns','type','details']

class BaseEditInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','dns','type','details']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(BaseEditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(ip_type=IpType.objects.filter(need_infra=False))
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True).filter(ip_type=IpType.objects.filter(need_infra=False)).filter(need_infra=False)
        else:
            self.fields['ipv4'].queryset = IpList.objects.filter(interface__isnull=True)

class AliasForm(ModelForm):
    class Meta:
        model = Alias
        fields = ['alias','extension']

    def __init__(self, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(AliasForm, self).__init__(*args, **kwargs)
        if not infra:
            self.fields['extension'].queryset = Extension.objects.filter(need_infra=False)
 
class DelAliasForm(ModelForm):
    alias = forms.ModelMultipleChoiceField(queryset=Alias.objects.all(), label="Alias actuels",  widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        interface = kwargs.pop('interface')
        super(DelAliasForm, self).__init__(*args, **kwargs)
        self.fields['alias'].queryset = Alias.objects.filter(interface_parent=interface)

    class Meta:
        exclude = ['interface_parent', 'alias', 'extension']
        model = Alias

class MachineTypeForm(ModelForm):
    class Meta:
        model = MachineType
        fields = ['type','ip_type']

    def __init__(self, *args, **kwargs):
        super(MachineTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type de machine à ajouter'
        self.fields['ip_type'].label = "Type d'ip relié"

class DelMachineTypeForm(ModelForm):
    machinetypes = forms.ModelMultipleChoiceField(queryset=MachineType.objects.all(), label="Types de machines actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['type','ip_type']
        model = MachineType

class IpTypeForm(ModelForm):
    class Meta:
        model = IpType
        fields = ['type','extension','need_infra','domaine_ip','domaine_range']

    def __init__(self, *args, **kwargs):
        super(IpTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type ip à ajouter'

class DelIpTypeForm(ModelForm):
    iptypes = forms.ModelMultipleChoiceField(queryset=IpType.objects.all(), label="Types d'ip actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['type','extension','need_infra','domaine_ip','domaine_range']
        model = IpType


class ExtensionForm(ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'need_infra', 'origin']

    def __init__(self, *args, **kwargs):
        super(ExtensionForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Extension à ajouter'
        self.fields['origin'].label = 'Enregistrement A origin'

class DelExtensionForm(ModelForm):
    extensions = forms.ModelMultipleChoiceField(queryset=Extension.objects.all(), label="Extensions actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['name', 'need_infra', 'origin']
        model = Extension

class MxForm(ModelForm):
    class Meta:
        model = Mx
        fields = ['zone', 'priority', 'name']
        
class DelMxForm(ModelForm):
    mx = forms.ModelMultipleChoiceField(queryset=Mx.objects.all(), label="MX actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['zone', 'priority', 'name']
        model = Mx

class NsForm(ModelForm):
    class Meta:
        model = Ns
        fields = ['zone', 'interface']

class DelNsForm(ModelForm):
    ns = forms.ModelMultipleChoiceField(queryset=Ns.objects.all(), label="Enregistrements NS actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['zone', 'interface']
        model = Ns
