from django.db import models
from macaddress.fields import MACAddressField

from users.models import User

class Machine(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    type = models.ForeignKey('MachineType', on_delete=models.PROTECT)

    def __str__(self):
        return self.type

class MachineType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type


class Interface(models.Model):
    ipv4 = models.OneToOneField('IpList', on_delete=models.PROTECT, blank=True, null=True)
    ipv6 = models.GenericIPAddressField(protocol='IPv6')
    mac_address = MACAddressField()
    machine = models.ForeignKey('Machine', on_delete=models.PROTECT)
    details = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return self.name

class IpList(models.Model):
    ipv4 = models.GenericIPAddressField(protocol='IPv4')

    def __str__(self):
        return self.type
