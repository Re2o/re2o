from django.db import models
from django.forms import ModelForm, Form, ValidationError
from macaddress.fields import MACAddressField

from users.models import User
from django.conf import settings
import re

def full_domain_validator(hostname):
    """ Validation du nom de domaine, extensions dans settings, prefixe pas plus long que 63 caractères """
    HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
    if not any(ext in hostname for ext in settings.ALLOWED_EXTENSIONS):
        raise ValidationError(
                ", le nom de domaine '%(label)s' doit comporter une extension valide",
                params={'label': hostname},
        )
    for extension in settings.ALLOWED_EXTENSIONS:
        if hostname.endswith(extension):
            hostname=re.sub('%s$' % extension, '', hostname) 
            break
    if len(hostname) > 63:
        raise ValidationError(
                ", le nom de domaine '%(label)s' est trop long (maximum de 63 caractères).",
                params={'label': hostname},
        )
    if not HOSTNAME_LABEL_PATTERN.match(hostname):
        raise ValidationError(
                ", ce nom de domaine '%(label)s' contient des carractères interdits.",
                params={'label': hostname},
        )

class Machine(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, help_text="Optionnel", blank=True, null=True)
    active = models.BooleanField(default=True)

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
    dns = models.CharField(help_text="Obligatoire et unique, doit se terminer en %s et ne pas comporter d'autres points" % ", ".join(settings.ALLOWED_EXTENSIONS), max_length=255, unique=True, validators=[full_domain_validator])

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
        self.fields['type'].empty_label = "Séléctionner un type de machine"

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
