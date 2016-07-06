from .models import Port
from django.forms import ModelForm, Form

class PortForm(ModelForm):
    class Meta:
        model = Port
        fields = '__all__'

class EditPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['room', 'machine_interface', 'related', 'details']
