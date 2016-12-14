from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from macaddress.fields import MACAddressField
from netaddr import mac_bare, EUI
from django.core.validators import MinValueValidator,MaxValueValidator

from re2o.settings import MAIN_EXTENSION


class Machine(models.Model):
    PRETTY_NAME = "Machine"
    
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, help_text="Optionnel", blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + ' - ' + str(self.id) + ' - ' +  str(self.name)

class MachineType(models.Model):
    PRETTY_NAME = "Type de machine"

    type = models.CharField(max_length=255)
    ip_type = models.ForeignKey('IpType', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
         return self.type

class IpType(models.Model):
    PRETTY_NAME = "Type d'ip"

    type = models.CharField(max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)
    domaine_ip = models.GenericIPAddressField(protocol='IPv4')
    domaine_range = models.IntegerField(validators=[MinValueValidator(8), MaxValueValidator(32)])

    def __str__(self):
        return self.type

class Extension(models.Model):
    PRETTY_NAME = "Extensions dns"

    name = models.CharField(max_length=255, unique=True)
    need_infra = models.BooleanField(default=False)
    origin = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.name

class Mx(models.Model):
    PRETTY_NAME = "Enregistrements MX"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    priority = models.IntegerField(unique=True)
    name = models.OneToOneField('Alias', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.priority) + ' ' + str(self.name)

class Ns(models.Model):
    PRETTY_NAME = "Enregistrements NS"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    interface = models.OneToOneField('Interface', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.interface)

class Interface(models.Model):
    PRETTY_NAME = "Interface"

    ipv4 = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)
    #ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
    mac_address = MACAddressField(integer=False, unique=True)
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    dns = models.CharField(help_text="Obligatoire et unique, ne doit pas comporter de points", max_length=255, unique=True)

    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    def mac_bare(self):
        return str(EUI(self.mac_address, dialect=mac_bare)).lower()

    def clean(self, *args, **kwargs):
        self.mac_address = str(EUI(self.mac_address)) or None
        if self.ipv4:
            alias = Alias.objects.filter(alias=self.dns).filter(extension=self.ipv4.ip_type.extension)
        else:
            alias = Alias.objects.filter(alias=self.dns)
        if alias:
            raise ValidationError("Impossible, le dns est déjà utilisé par un alias (%s)" % alias[0])

    def __str__(self):
        return self.dns

class Alias(models.Model):
    PRETTY_NAME = "Alias dns"

    interface_parent = models.ForeignKey('Interface', on_delete=models.CASCADE)
    alias = models.CharField(help_text="Obligatoire et unique, ne doit pas comporter de points", max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)

    class Meta:
        unique_together = ("alias", "extension")

    def clean(self, *args, **kwargs):
        if hasattr(self, 'alias') and hasattr(self, 'extension'):
            if Interface.objects.filter(dns=self.alias).filter(ipv4=IpList.objects.filter(ip_type=IpType.objects.filter(extension=self.extension))):
                raise ValidationError("Impossible d'ajouter l'alias, déjà utilisé par une machine")

    def __str__(self):
        return str(self.alias) + str(self.extension)

class IpList(models.Model):
    PRETTY_NAME = "Addresses ipv4"

    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ip_type = models.ForeignKey('IpType', on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)

    def __str__(self):
        return self.ipv4


@receiver(post_save, sender=Interface)
def interface_post_save(sender, **kwargs):
    user = kwargs['instance'].machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_delete, sender=Interface)
def interface_post_delete(sender, **kwargs):
    interface = kwargs['instance']
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

