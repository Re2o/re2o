from .models import Port, Switch, Room
from django.forms import ModelForm, Form

class PortForm(ModelForm):
    class Meta:
        model = Port
        fields = '__all__'

class EditPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['room', 'machine_interface', 'related', 'details']

    def __init__(self, *args, **kwargs):
        super(EditPortForm, self).__init__(*args, **kwargs)
        self.fields['related'].queryset = Port.objects.all().order_by('switch', 'port')

class AddPortForm(ModelForm):
    class Meta(PortForm.Meta):
        fields = ['port', 'room', 'machine_interface', 'related', 'details']

class EditSwitchForm(ModelForm):
    class Meta:
        model = Switch
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditSwitchForm, self).__init__(*args, **kwargs)
        self.fields['location'].label = 'Localisation'
        self.fields['number'].label = 'Nombre de ports'

class NewSwitchForm(ModelForm):
    class Meta(EditSwitchForm.Meta):
        fields = ['location', 'number', 'details']

class EditRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
