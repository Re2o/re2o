from django.db import models
from django.forms import ModelForm, Form
from macaddress.fields import MACAddressField

from users.models import User

class Machine(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, help_text="Optionnel", blank=True, null=True)

    def __str__(self):
        return str(self.user) + ' - ' + str(self.id) + ' - ' +  str(self.name)

class MachineType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type


class Interface(models.Model):
    ipv4 = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)
    #ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
    mac_address = MACAddressField(integer=False, unique=True)
    machine = models.ForeignKey('Machine', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    dns = models.CharField(help_text="Obligatoire et unique", max_length=255, unique=True)

    def __str__(self):
        return self.dns

class IpList(models.Model):
    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)

    def __str__(self):
        return self.ipv4

class EditMachineForm(ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditMachineForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom de la machine'
        self.fields['type'].label = 'Type de machine'

class NewMachineForm(EditMachineForm):
    class Meta(EditMachineForm.Meta):
        fields = ['type','name']

class EditInterfaceForm(ModelForm):
    class Meta:
        model = Interface
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['dns'].label = 'Nom dns de la machine'
        self.fields['mac_address'].label = 'Adresse mac'

class AddInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','dns','details']

class NewInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['mac_address','dns','details']
