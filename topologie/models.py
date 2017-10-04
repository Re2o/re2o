# -*- mode: python; coding: utf-8 -*-
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

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.forms import ModelForm, Form
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
import reversion

from machines.models import Vlan

def make_port_related(port):
    related_port = port.related
    related_port.related = port
    related_port.save()
    
def clean_port_related(port):
    related_port = port.related_port
    related_port.related = None
    related_port.save()

class Stack(models.Model):
    PRETTY_NAME = "Stack de switchs"

    name = models.CharField(max_length=32, blank=True, null=True)
    stack_id = models.CharField(max_length=32, unique=True)
    details = models.CharField(max_length=255, blank=True, null=True)
    member_id_min = models.IntegerField()
    member_id_max = models.IntegerField()

    def __str__(self):
        return " ".join([self.name, self.stack_id])

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.stack_id
        super(Stack, self).save(*args, **kwargs)

    def clean(self):
        if self.member_id_max < self.member_id_min:
            raise ValidationError({'member_id_max':"L'id maximale est inférieure à l'id minimale"})

class Switch(models.Model):
    PRETTY_NAME = "Switch / Commutateur"

    switch_interface = models.OneToOneField('machines.Interface', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    number = models.IntegerField()
    details = models.CharField(max_length=255, blank=True)
    stack = models.ForeignKey(Stack, blank=True, null=True, on_delete=models.SET_NULL)
    stack_member_id = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('stack','stack_member_id')

    def __str__(self):
        return str(self.location) + ' ' + str(self.switch_interface)

    def clean(self):
        if self.stack is not None:
            if self.stack_member_id is not None:
                if (self.stack_member_id > self.stack.member_id_max) or (self.stack_member_id < self.stack.member_id_min):
                    raise ValidationError({'stack_member_id': "L'id de ce switch est en dehors des bornes permises pas la stack"})
            else:
                raise ValidationError({'stack_member_id': "L'id dans la stack ne peut être nul"})

class Port(models.Model):
    PRETTY_NAME = "Port de switch"
    STATES = (
            ('NO', 'NO'),
            ('STRICT', 'STRICT'),
            ('BLOQ', 'BLOQ'),
            ('COMMON', 'COMMON'),
            )
    
    switch = models.ForeignKey('Switch', related_name="ports")
    port = models.IntegerField()
    room = models.ForeignKey('Room', on_delete=models.PROTECT, blank=True, null=True)
    machine_interface = models.ForeignKey('machines.Interface', on_delete=models.SET_NULL, blank=True, null=True)
    related = models.OneToOneField('self', null=True, blank=True, related_name='related_port')
    radius = models.CharField(max_length=32, choices=STATES, default='NO')
    vlan_force = models.ForeignKey('machines.Vlan', on_delete=models.SET_NULL, blank=True, null=True)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('switch', 'port')

    def clean(self):
        if hasattr(self, 'switch'):
            if self.port > self.switch.number:
                raise ValidationError("Ce port ne peut exister, numero trop élevé")
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
    PRETTY_NAME = "Chambre/ Prise murale"

    name = models.CharField(max_length=255, unique=True)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return str(self.name)

@receiver(post_delete, sender=Stack)
def stack_post_delete(sender, **kwargs):
    Switch.objects.filter(stack=None).update(stack_member_id = None)
