from django.db import models
from django.forms import ValidationError
from macaddress.fields import MACAddressField

class Machine(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, help_text="Optionnel", blank=True, null=True)
    active = models.BooleanField(default=True)

    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = machine.user
        return machine.active and user.has_access()

    def __str__(self):
        return str(self.user) + ' - ' + str(self.id) + ' - ' +  str(self.name)

class MachineType(models.Model):
    type = models.CharField(max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)

    def __str__(self):
        return self.type

class Extension(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Interface(models.Model):
    ipv4 = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)
    #ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
    mac_address = MACAddressField(integer=False, unique=True)
    machine = models.ForeignKey('Machine', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    dns = models.CharField(help_text="Obligatoire et unique, doit se terminer en %s et ne pas comporter d'autres points" % ", ".join(Extension.objects.values_list('name', flat=True)), max_length=255, unique=True)

    def __str__(self):
        return self.dns

class IpList(models.Model):
    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)

    def __str__(self):
        return self.ipv4

