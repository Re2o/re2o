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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from django.forms import ValidationError
from django.core.validators import MinValueValidator

from django.db.models import Max
from django.utils import timezone

from machines.models import regen

class Facture(models.Model):
    PRETTY_NAME = "Factures émises"

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    banque = models.ForeignKey('Banque', on_delete=models.PROTECT, blank=True, null=True)
    cheque = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)
    control = models.BooleanField(default=False)

    def prix(self):
        prix = Vente.objects.filter(facture=self).aggregate(models.Sum('prix'))['prix__sum']
        return prix

    def prix_total(self):
        return Vente.objects.filter(facture=self).aggregate(total=models.Sum(models.F('prix')*models.F('number'), output_field=models.FloatField()))['total']

    def name(self):
        name = ' - '.join(Vente.objects.filter(facture=self).values_list('name', flat=True))
        return name

    def __str__(self):
        return str(self.user) + ' ' + str(self.date)

@receiver(post_save, sender=Facture)
def facture_post_save(sender, **kwargs):
    facture = kwargs['instance']
    user = facture.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)

@receiver(post_delete, sender=Facture)
def facture_post_delete(sender, **kwargs):
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)

class Vente(models.Model):
    PRETTY_NAME = "Ventes effectuées"

    facture = models.ForeignKey('Facture', on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(1)])
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    iscotisation = models.BooleanField()
    duration = models.IntegerField(help_text="Durée exprimée en mois entiers", blank=True, null=True)

    def prix_total(self):
        return self.prix*self.number

    def update_cotisation(self):
        if hasattr(self, 'cotisation'):
            cotisation = self.cotisation
            cotisation.date_end = cotisation.date_start + relativedelta(months=self.duration*self.number)
        return

    def create_cotis(self, date_start=False):
        """ Update et crée l'objet cotisation associé à une facture, prend en argument l'user, la facture pour la quantitéi, et l'article pour la durée"""
        if not hasattr(self, 'cotisation'):
            cotisation=Cotisation(vente=self)
            if date_start:
                end_adhesion = Cotisation.objects.filter(vente__in=Vente.objects.filter(facture__in=Facture.objects.filter(user=self.facture.user).exclude(valid=False))).filter(date_start__lt=date_start).aggregate(Max('date_end'))['date_end__max']
            else:
                end_adhesion = self.facture.user.end_adhesion()
            date_start = date_start or timezone.now()
            end_adhesion = end_adhesion or date_start
            date_max = max(end_adhesion, date_start)
            cotisation.date_start = date_max
            cotisation.date_end = cotisation.date_start + relativedelta(months=self.duration*self.number) 
        return

    def save(self, *args, **kwargs):
        # On verifie que si iscotisation, duration est présent
        if self.iscotisation and not self.duration:
            raise ValidationError("Cotisation et durée doivent être présents ensembles")
        self.update_cotisation()
        super(Vente, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)

@receiver(post_save, sender=Vente)
def vente_post_save(sender, **kwargs):
    vente = kwargs['instance']
    if hasattr(vente, 'cotisation'):
        vente.cotisation.vente = vente
        vente.cotisation.save()
    if vente.iscotisation:
        vente.create_cotis()
        vente.cotisation.save()
        user = vente.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)

@receiver(post_delete, sender=Vente)
def vente_post_delete(sender, **kwargs):
    vente = kwargs['instance']
    if vente.iscotisation:
        user = vente.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)

class Article(models.Model):
    PRETTY_NAME = "Articles en vente"

    name = models.CharField(max_length=255, unique=True)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    iscotisation = models.BooleanField()
    duration = models.IntegerField(
        help_text="Durée exprimée en mois entiers",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])

    def clean(self):
        if self.name.lower() == "solde":
            raise ValidationError("Solde est un nom d'article invalide")

    def __str__(self):
        return self.name

class Banque(models.Model):
    PRETTY_NAME = "Banques enregistrées"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Paiement(models.Model):
    PRETTY_NAME = "Moyens de paiement"
    PAYMENT_TYPES = (
        (0, 'Autre'),
        (1, 'Chèque'),
    )

    moyen = models.CharField(max_length=255)
    type_paiement = models.IntegerField(choices=PAYMENT_TYPES, default=0)

    def __str__(self):
        return self.moyen

    def clean(self):
        self.moyen = self.moyen.title()

    def save(self, *args, **kwargs):
        if Paiement.objects.filter(type_paiement=1).count() > 1:
            raise ValidationError("On ne peut avoir plusieurs mode de paiement chèque")
        super(Paiement, self).save(*args, **kwargs)

class Cotisation(models.Model):
    PRETTY_NAME = "Cotisations"

    vente = models.OneToOneField('Vente', on_delete=models.CASCADE, null=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return str(self.vente)

@receiver(post_save, sender=Cotisation)
def cotisation_post_save(sender, **kwargs):
    regen('dns')
    regen('dhcp')
    regen('mac_ip_list')
    regen('mailing')

@receiver(post_delete, sender=Cotisation)
def vente_post_delete(sender, **kwargs):
    cotisation = kwargs['instance']
    regen('mac_ip_list')
    regen('mailing')
