from django.db import models
from django.forms import ModelForm, Form
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError

def make_port_related(port):
    related_port = port.related
    related_port.related = port
    related_port.save()
    
def clean_port_related(port):
    related_port = port.related_port
    related_port.related = None
    related_port.save()

class Switch(models.Model):
    building = models.CharField(max_length=10)
    number = models.IntegerField()
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('building', 'number')

    def __str__(self):
        return str(self.building) + str(self.number)

class Port(models.Model):
    switch = models.ForeignKey('Switch', related_name="ports")
    port = models.IntegerField()
    room = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True, null=True)
    machine_interface = models.OneToOneField('machines.Interface', on_delete=models.PROTECT, blank=True, null=True)
    related = models.OneToOneField('self', null=True, blank=True, related_name='related_port')
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('switch', 'port')

    def clean(self):
        if self.room and self.machine_interface or self.room and self.related or self.machine_interface and self.related:
            raise ValidationError("Chambre, interface et related_port sont mutuellement exclusifs")
        if self.related==self:
            raise ValidationError("On ne peut relier un port à lui même")
        if self.related and not self.related.related:
            if self.related.machine_interface or self.related.room:
                raise ValidationError("Le port relié est déjà occupé, veuillez le libérer avant de créer une relation")
            else:
                make_port_related(self)
        elif hasattr(self, 'related_port'):
            clean_port_related(self)

    def __str__(self):
        return str(self.switch) + " - " + str(self.port)

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.name)

