from django.db import models

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
