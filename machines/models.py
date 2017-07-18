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

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from macaddress.fields import MACAddressField
from netaddr import mac_bare, EUI
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils.functional import cached_property

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
    name = models.OneToOneField('Domain', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.priority) + ' ' + str(self.name)

class Ns(models.Model):
    PRETTY_NAME = "Enregistrements NS"

    zone = models.ForeignKey('Extension', on_delete=models.PROTECT)
    ns = models.OneToOneField('Domain', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.zone) + ' ' + str(self.ns)

class Interface(models.Model):
    PRETTY_NAME = "Interface"

    ipv4 = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)
    #ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
    mac_address = MACAddressField(integer=False, unique=True)
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)

    @cached_property
    def is_active(self):
        """ Renvoie si une interface doit avoir accès ou non """
        machine = self.machine
        user = self.machine.user
        return machine.active and user.has_access()

    def mac_bare(self):
        return str(EUI(self.mac_address, dialect=mac_bare)).lower()

    def clean(self, *args, **kwargs):
        self.mac_address = str(EUI(self.mac_address)) or None

    def __str__(self):
        try:
            domain = self.domain
        except:
            domain = None
        return str(domain)

class Domain(models.Model):
    PRETTY_NAME = "Domaine dns"

    interface_parent = models.OneToOneField('Interface', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(help_text="Obligatoire et unique, ne doit pas comporter de points", max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    cname = models.ForeignKey('self', null=True, blank=True, related_name='related_domain')

    class Meta:
        unique_together = ("name", "extension")

    def clean(self):
        if self.interface_parent and self.cname:
            raise ValidationError("On ne peut créer à la fois A et CNAME")
        if self.cname==self:
            raise ValidationError("On ne peut créer un cname sur lui même")

    def __str__(self):
        return str(self.name) + str(self.extension)

class IpList(models.Model):
    PRETTY_NAME = "Addresses ipv4"

    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ip_type = models.ForeignKey('IpType', on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)

    def __str__(self):
        return self.ipv4

@receiver(post_save, sender=Machine)
def machine_post_save(sender, **kwargs):
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_delete, sender=Machine)
def machine_post_delete(sender, **kwargs):
    machine = kwargs['instance']
    user = machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_save, sender=Interface)
def interface_post_save(sender, **kwargs):
    user = kwargs['instance'].machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_delete, sender=Interface)
def interface_post_delete(sender, **kwargs):
    interface = kwargs['instance']
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

