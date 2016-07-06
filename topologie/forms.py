from .models import Port, Switch
from django.forms import ModelForm, Form

class PortForm(ModelForm):
    class Meta:
        model = Port
        fields = '__all__'

class EditPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['room', 'machine_interface', 'related', 'details']

class AddPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['port', 'room', 'machine_interface', 'related', 'details']

class SwitchForm(ModelForm):
    class Meta:
        model = Switch
        fields = '__all__'

class EditSwitchForm(ModelForm):
    class Meta(SwitchForm.Meta):
        fields = ['building', 'number', 'details']

