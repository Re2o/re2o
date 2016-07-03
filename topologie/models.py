from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
 

class Switch(models.Model):
    building = models.CharField(max_length=10)
    number = models.IntegerField()
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('building', 'number')

    def __str__(self):
        return str(self.building) + str(self.number)

class Port(models.Model):
    switch = models.ForeignKey(Switch, related_name="ports")
    port = models.IntegerField()
    details = models.CharField(max_length=255, blank=True)
    room = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        unique_together = ('_content_type', '_object_id')

    _content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    _object_id = models.PositiveIntegerField(blank=True, null=True)
    goto = GenericForeignKey('_content_type', '_object_id')
 
    @property
    def comefrom(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            event = Port.objects.get(_content_type__pk=ctype.id, _object_id=self.id)
        except:
            return None
        return event

    def __str__(self):
        return str(self.switch) + " - " + str(self.port)

class Room(models.Model):
    details = models.CharField(max_length=255, blank=True)
    building = models.CharField(max_length=255)
    room = models.IntegerField()
    number = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('building', 'room', 'number')

    def __str__(self):
        return str(self.building) + str(self.room) + '-' + str(self.number)

