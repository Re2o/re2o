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
"""
Definition des modèles de l'application topologie.

On défini les models suivants :

- stack (id, id_min, id_max et nom) regrouppant les switches
- switch : nom, nombre de port, et interface
machine correspondante (mac, ip, etc) (voir machines.models.interface)
- Port: relié à un switch parent par foreign_key, numero du port,
relié de façon exclusive à un autre port, une machine
(serveur ou borne) ou une prise murale
- room : liste des prises murales, nom et commentaire de l'état de
la prise
"""

from __future__ import unicode_literals

import itertools

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import transaction
from reversion import revisions as reversion


class Stack(models.Model):
    """Un objet stack. Regrouppe des switchs en foreign key
    ,contient une id de stack, un switch id min et max dans
    le stack"""
    PRETTY_NAME = "Stack de switchs"

    name = models.CharField(max_length=32, blank=True, null=True)
    stack_id = models.CharField(max_length=32, unique=True)
    details = models.CharField(max_length=255, blank=True, null=True)
    member_id_min = models.PositiveIntegerField()
    member_id_max = models.PositiveIntegerField()

    def __str__(self):
        return " ".join([self.name, self.stack_id])

    def save(self, *args, **kwargs):
        self.clean()
        if not self.name:
            self.name = self.stack_id
        super(Stack, self).save(*args, **kwargs)

    def clean(self):
        """ Verification que l'id_max < id_min"""
        if self.member_id_max < self.member_id_min:
            raise ValidationError({'member_id_max': "L'id maximale est\
                inférieure à l'id minimale"})


class Switch(models.Model):
    """ Definition d'un switch. Contient un nombre de ports (number),
    un emplacement (location), un stack parent (optionnel, stack)
    et un id de membre dans le stack (stack_member_id)
    relié en onetoone à une interface
    Pourquoi ne pas avoir fait hériter switch de interface ?
    Principalement par méconnaissance de la puissance de cette façon de faire.
    Ceci étant entendu, django crée en interne un onetoone, ce qui a un
    effet identique avec ce que l'on fait ici

    Validation au save que l'id du stack est bien dans le range id_min
    id_max de la stack parente"""
    PRETTY_NAME = "Switch / Commutateur"

    switch_interface = models.OneToOneField(
        'machines.Interface',
        on_delete=models.CASCADE
        )
    location = models.CharField(max_length=255)
    number = models.PositiveIntegerField()
    details = models.CharField(max_length=255, blank=True)
    stack = models.ForeignKey(
        'topologie.Stack',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
        )
    stack_member_id = models.PositiveIntegerField(blank=True, null=True)
    model = models.ForeignKey(
        'topologie.ModelSwitch',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ('stack', 'stack_member_id')

    def __str__(self):
        return str(self.location) + ' ' + str(self.switch_interface)

    def clean(self):
        """ Verifie que l'id stack est dans le bon range"""
        if self.stack is not None:
            if self.stack_member_id is not None:
                if (self.stack_member_id > self.stack.member_id_max) or\
                        (self.stack_member_id < self.stack.member_id_min):
                    raise ValidationError(
                        {'stack_member_id': "L'id de ce switch est en\
                            dehors des bornes permises pas la stack"}
                        )
            else:
                raise ValidationError({'stack_member_id': "L'id dans la stack\
                    ne peut être nul"})
    def create_ports(self, begin, end):
        """ Crée les ports de begin à end si les valeurs données sont cohérentes. """

        s_begin = s_end = 0
        nb_ports = self.ports.count()
        if nb_ports > 0:
            ports = self.ports.order_by('port').values('port')
            s_begin = ports.first().get('port')
            s_end = ports.last().get('port')

        if end < begin:
            raise ValidationError("Port de fin inférieur au port de début !")
        if end - begin > self.number:
            raise ValidationError("Ce switch ne peut avoir autant de ports.")
        begin_range = range(begin, s_begin)
        end_range = range(s_end+1, end+1)
        for i in itertools.chain(begin_range, end_range):
            port = Port()
            port.switch = self
            port.port = i
            try:
                with transaction.atomic(), reversion.create_revision():
                    port.save()
                    reversion.set_comment("Création")
            except IntegrityError:
                ValidationError("Création d'un port existant.")


class ModelSwitch(models.Model):
    """Un modèle (au sens constructeur) de switch"""
    PRETTY_NAME = "Modèle de switch"
    reference = models.CharField(max_length=255)
    constructor = models.ForeignKey(
        'topologie.ConstructorSwitch',
        on_delete=models.PROTECT
    )

    def __str__(self):
        return str(self.constructor) + ' ' + str(self.reference)


class ConstructorSwitch(models.Model):
    """Un constructeur de switch"""
    PRETTY_NAME = "Constructeur de switch"
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class Port(models.Model):
    """ Definition d'un port. Relié à un switch(foreign_key),
    un port peut etre relié de manière exclusive à :
    - une chambre (room)
    - une machine (serveur etc) (machine_interface)
    - un autre port (uplink) (related)
    Champs supplémentaires :
    - RADIUS (mode STRICT : connexion sur port uniquement si machine
    d'un adhérent à jour de cotisation et que la chambre est également à
    jour de cotisation
    mode COMMON : vérification uniquement du statut de la machine
    mode NO : accepte toute demande venant du port et place sur le vlan normal
    mode BLOQ : rejet de toute authentification
    - vlan_force : override la politique générale de placement vlan, permet
    de forcer un port sur un vlan particulier. S'additionne à la politique
    RADIUS"""
    PRETTY_NAME = "Port de switch"
    STATES = (
        ('NO', 'NO'),
        ('STRICT', 'STRICT'),
        ('BLOQ', 'BLOQ'),
        ('COMMON', 'COMMON'),
        )

    switch = models.ForeignKey(
        'Switch',
        related_name="ports",
        on_delete=models.CASCADE
    )
    port = models.PositiveIntegerField()
    room = models.ForeignKey(
        'Room',
        on_delete=models.PROTECT,
        blank=True,
        null=True
        )
    machine_interface = models.ForeignKey(
        'machines.Interface',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )
    related = models.OneToOneField(
        'self',
        null=True,
        blank=True,
        related_name='related_port'
        )
    radius = models.CharField(max_length=32, choices=STATES, default='NO')
    vlan_force = models.ForeignKey(
        'machines.Vlan',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('switch', 'port')

    def make_port_related(self):
        """ Synchronise le port distant sur self"""
        related_port = self.related
        related_port.related = self
        related_port.save()

    def clean_port_related(self):
        """ Supprime la relation related sur self"""
        related_port = self.related_port
        related_port.related = None
        related_port.save()

    def clean(self):
        """ Verifie que un seul de chambre, interface_parent et related_port
        est rempli. Verifie que le related n'est pas le port lui-même....
        Verifie que le related n'est pas déjà occupé par une machine ou une
        chambre. Si ce n'est pas le cas, applique la relation related
        Si un port related point vers self, on nettoie la relation
        A priori pas d'autre solution que de faire ça à la main. A priori
        tout cela est dans un bloc transaction, donc pas de problème de
        cohérence"""
        if hasattr(self, 'switch'):
            if self.port > self.switch.number:
                raise ValidationError("Ce port ne peut exister,\
                    numero trop élevé")
        if self.room and self.machine_interface or self.room and\
                self.related or self.machine_interface and self.related:
            raise ValidationError("Chambre, interface et related_port sont\
                mutuellement exclusifs")
        if self.related == self:
            raise ValidationError("On ne peut relier un port à lui même")
        if self.related and not self.related.related:
            if self.related.machine_interface or self.related.room:
                raise ValidationError("Le port relié est déjà occupé, veuillez\
                    le libérer avant de créer une relation")
            else:
                self.make_port_related()
        elif hasattr(self, 'related_port'):
            self.clean_port_related()

    def __str__(self):
        return str(self.switch) + " - " + str(self.port)


class Room(models.Model):
    """Une chambre/local contenant une prise murale"""
    PRETTY_NAME = "Chambre/ Prise murale"

    name = models.CharField(max_length=255, unique=True)
    details = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)


@receiver(post_delete, sender=Stack)
def stack_post_delete(sender, **kwargs):
    """Vide les id des switches membres d'une stack supprimée"""
    Switch.objects.filter(stack=None).update(stack_member_id=None)
