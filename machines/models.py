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
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils.functional import cached_property
from macaddress.fields import MACAddressField
from netaddr import mac_bare, EUI, IPSet, IPNetwork
from django.core.validators import MinValueValidator,MaxValueValidator
import re
from reversion import revisions as reversion

from re2o.settings import MAIN_EXTENSION

class Machine(models.Model):
    """ Class définissant une machine, object parent user, objets fils interfaces"""
    PRETTY_NAME = "Machine"
    
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, help_text="Optionnel", blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + ' - ' + str(self.id) + ' - ' +  str(self.name)

class MachineType(models.Model):
    """ Type de machine, relié à un type d'ip, affecté aux interfaces"""
    PRETTY_NAME = "Type de machine"

    type = models.CharField(max_length=255)
    ip_type = models.ForeignKey('IpType', on_delete=models.PROTECT, blank=True, null=True)

    def all_interfaces(self):
        return Interface.objects.filter(type=self)

    def __str__(self):
         return self.type

class IpType(models.Model):
    """ Type d'ip, définissant un range d'ip, affecté aux machine types"""
    PRETTY_NAME = "Type d'ip"

    type = models.CharField(max_length=255)
    extension = models.ForeignKey('Extension', on_delete=models.PROTECT)
    need_infra = models.BooleanField(default=False)
    domaine_ip = models.GenericIPAddressField(protocol='IPv4')
    domaine_range = models.IntegerField(validators=[MinValueValidator(8), MaxValueValidator(32)])

    @cached_property
    def network(self):
        return str(self.domaine_ip) + '/' + str(self.domaine_range)

    @cached_property
    def ip_network(self):
        return IPNetwork(self.network)

    @cached_property
    def ip_set(self):
        return IPSet(self.ip_network)

    @cached_property
    def ip_set_as_str(self):
        return [str(x) for x in self.ip_set]

    def ip_objects(self):
        return IpList.objects.filter(ip_type=self)

    def free_ip(self):
        return IpList.objects.filter(interface__isnull=True).filter(ip_type=self)

    def gen_ip_range(self):
        # Creation du range d'ip dans les objets iplist
        for ip in self.ip_network.iter_hosts():
            obj, created = IpList.objects.get_or_create(ip_type=self, ipv4=str(ip))

    def del_ip_range(self):
        """ Methode dépréciée, IpList est en mode cascade et supprimé automatiquement"""
        if Interface.objects.filter(ipv4__in=self.ip_objects()):
            raise ValidationError("Une ou plusieurs ip du range sont affectées, impossible de supprimer le range")
        for ip in self.ip_objects():
            ip.delete()

    def clean(self):
        # On check que les / ne se recoupent pas
        for element in IpType.objects.all():
            if not self.ip_set.isdisjoint(element.ip_set):
                raise ValidationError("Le range indiqué n'est pas disjoint des ranges existants")
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpType, self).save(*args, **kwargs)

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
        if not self.ipv4 or self.type.ip_type != self.ipv4.ip_type:
            self.assign_ipv4()

    def assign_ipv4(self):
        """ Assigne une ip à l'interface """
        free_ips = self.type.ip_type.free_ip()
        if free_ips:
            self.ipv4 = free_ips[0]
        else:
            raise ValidationError("Il n'y a plus d'ip disponibles dans le slash")
        return

    def unassign_ipv4(self):
        self.ipv4 = None

    def update_type(self):
        """ Lorsque le machinetype est changé de type d'ip, on réassigne"""
        self.clean()
        self.save()

    def save(self, *args, **kwargs):
        self.mac_address = str(EUI(self.mac_address)) or None
        # On verifie la cohérence en forçant l'extension par la méthode
        if self.type.ip_type != self.ipv4.ip_type:
             raise ValidationError("L'ipv4 et le type de la machine ne correspondent pas")
        super(Interface, self).save(*args, **kwargs)

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
        unique_together = (("name", "extension"),)

    def get_extension(self):
        if self.interface_parent:
            return self.interface_parent.type.ip_type.extension
        elif hasattr(self,'extension'):
            return self.extension
        else:
            return None

    def clean(self):
        if self.get_extension():
            self.extension=self.get_extension()
        """ Validation du nom de domaine, extensions dans type de machine, prefixe pas plus long que 63 caractères """
        if self.interface_parent and self.cname:
            raise ValidationError("On ne peut créer à la fois A et CNAME")
        if self.cname==self:
            raise ValidationError("On ne peut créer un cname sur lui même")
        HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
        dns = self.name.lower()
        if len(dns) > 63:
            raise ValidationError("Le nom de domaine %s est trop long (maximum de 63 caractères)." % dns)
        if not HOSTNAME_LABEL_PATTERN.match(dns):
            raise ValidationError("Ce nom de domaine %s contient des carractères interdits." % dns)
        self.validate_unique()
        super(Domain, self).clean()


    def save(self, *args, **kwargs):
        if not self.get_extension():
            raise ValidationError("Extension invalide")
        self.full_clean()
        super(Domain, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name) + str(self.get_extension())

class IpList(models.Model):
    PRETTY_NAME = "Addresses ipv4"

    ipv4 = models.GenericIPAddressField(protocol='IPv4', unique=True)
    ip_type = models.ForeignKey('IpType', on_delete=models.CASCADE)

    @cached_property
    def need_infra(self):
        return self.ip_type.need_infra

    def clean(self):
        if not str(self.ipv4) in self.ip_type.ip_set_as_str:
            raise ValidationError("L'ipv4 et le range de l'iptype ne correspondent pas!")
        return

    def save(self, *args, **kwargs):
        self.clean()
        super(IpList, self).save(*args, **kwargs)

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
    interface = kwargs['instance']
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_delete, sender=Interface)
def interface_post_delete(sender, **kwargs):
    interface = kwargs['instance']
    user = interface.machine.user
    user.ldap_sync(base=False, access_refresh=False, mac_refresh=True)

@receiver(post_save, sender=IpType)
def iptype_post_save(sender, **kwargs):
    iptype = kwargs['instance']
    iptype.gen_ip_range()

@receiver(post_save, sender=MachineType)
def machine_post_save(sender, **kwargs):
    machinetype = kwargs['instance']
    for interface in machinetype.all_interfaces():
        interface.update_type()

