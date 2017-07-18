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
from dateutil.relativedelta import relativedelta
from django.forms import ValidationError
from django.core.validators import MinValueValidator


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
        name = ' - '.join(vente.name for vente in Vente.objects.filter(facture=self))
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

    def clean(self):
        if hasattr(self, 'cotisation'):
            cotisation = self.cotisation
            cotisation.date_end = cotisation.date_start + relativedelta(months=self.duration*self.number)
            cotisation.save()

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)

@receiver(post_save, sender=Vente)
def vente_post_save(sender, **kwargs):
    vente = kwargs['instance']
    if vente.iscotisation:
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
        min_value=0)

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

    moyen = models.CharField(max_length=255)

    def __str__(self):
        return self.moyen

    def clean(self):
        self.moyen = self.moyen.title()

class Cotisation(models.Model):
    PRETTY_NAME = "Cotisations"

    vente = models.OneToOneField('Vente', on_delete=models.CASCADE, null=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return str(self.vente)

