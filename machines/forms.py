from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import Machine, Interface, IpList, MachineType, Extension, IpType

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
            self.fields['ipv4'].queryset = IpList.objects.filter(ip_type=IpType.objects.filter(need_infra=False))

class NewInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['mac_address','dns','type','details']

class BaseEditInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','dns','type','details']

    def __init__(self, infra=False, *args, **kwargs):
        infra = kwargs.pop('infra')
        super(BaseEditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"
        if not infra:
            self.fields['type'].queryset = MachineType.objects.filter(IpType.objects.filter(need_infra=False))
            self.fields['ipv4'].queryset = IpList.objects.filter(ip_type=IpType.objects.filter(need_infra=False))

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
        fields = ['type','extension','need_infra']

    def __init__(self, *args, **kwargs):
        super(IpTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type ip à ajouter'

class DelIpTypeForm(ModelForm):
    iptypes = forms.ModelMultipleChoiceField(queryset=IpType.objects.all(), label="Types d'ip actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['type','extension','need_infra']
        model = IpType


class ExtensionForm(ModelForm):
    class Meta:
        model = Extension
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(ExtensionForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Exstension à ajouter'

class DelExtensionForm(ModelForm):
    extensions = forms.ModelMultipleChoiceField(queryset=Extension.objects.all(), label="Extensions actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['name']
        model = Extension
