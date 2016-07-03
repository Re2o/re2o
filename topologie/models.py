from django.db import models

class Port(models.Model):
    building = models.CharField(max_length=10)
    switch = models.IntegerField()
    port = models.IntegerField()
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("building", "switch", "port")

    def __str__(self):
        return str(self.building) + " - " + str(self.switch) + " - " + str(self.port)

class Room(models.Model):
    details = models.CharField(max_length=255, blank=True)
    room = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.room)

class Link(models.Model):
    port = models.ForeignKey('Port', on_delete=models.PROTECT)
    details = models.CharField(max_length=255, blank=True)
    #port_linked = models.ForeignKey('Port', on_delete=models.PROTECT, blank=True)
    room = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True)

    def __str__(self):
        return str(self.port) 
