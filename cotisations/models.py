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
Definition des models bdd pour les factures et cotisation.
Pièce maitresse : l'ensemble du code intelligent se trouve ici,
dans les clean et save des models ainsi que de leur methodes supplémentaires.

Facture : reliée à un user, elle a un moyen de paiement, une banque (option),
une ou plusieurs ventes

Article : liste des articles en vente, leur prix, etc

Vente : ensemble des ventes effectuées, reliées à une facture (foreignkey)

Banque : liste des banques existantes

Cotisation : objets de cotisation, contenant un début et une fin. Reliées
aux ventes, en onetoone entre une vente et une cotisation.
Crées automatiquement au save des ventes.

Post_save et Post_delete : sychronisation des services et régénération
des services d'accès réseau (ex dhcp) lors de la vente d'une cotisation
par exemple
"""

from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Max
from django.utils import timezone
from machines.models import regen


class Facture(models.Model):
    """ Définition du modèle des factures. Une facture regroupe une ou
    plusieurs ventes, rattachée à un user, et reliée à un moyen de paiement
    et si il y a lieu un numero pour les chèques. Possède les valeurs
    valides et controle (trésorerie)"""
    PRETTY_NAME = "Factures émises"

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    banque = models.ForeignKey(
        'Banque',
        on_delete=models.PROTECT,
        blank=True,
        null=True)
    cheque = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)
    control = models.BooleanField(default=False)

    def prix(self):
        """Renvoie le prix brut sans les quantités. Méthode
        dépréciée"""
        prix = Vente.objects.filter(
            facture=self
            ).aggregate(models.Sum('prix'))['prix__sum']
        return prix

    def prix_total(self):
        """Prix total : somme des produits prix_unitaire et quantité des
        ventes de l'objet"""
        return Vente.objects.filter(
            facture=self
            ).aggregate(
                total=models.Sum(
                    models.F('prix')*models.F('number'),
                    output_field=models.FloatField()
                )
            )['total']

    def name(self):
        """String, somme des name des ventes de self"""
        name = ' - '.join(Vente.objects.filter(
            facture=self
            ).values_list('name', flat=True))
        return name

    def __str__(self):
        return str(self.user) + ' ' + str(self.date)


@receiver(post_save, sender=Facture)
def facture_post_save(sender, **kwargs):
    """Post save d'une facture, synchronise l'user ldap"""
    facture = kwargs['instance']
    user = facture.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


@receiver(post_delete, sender=Facture)
def facture_post_delete(sender, **kwargs):
    """Après la suppression d'une facture, on synchronise l'user ldap"""
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


class Vente(models.Model):
    """Objet vente, contient une quantité, une facture parente, un nom,
    un prix. Peut-être relié à un objet cotisation, via le boolean
    iscotisation"""
    PRETTY_NAME = "Ventes effectuées"

    COTISATION_TYPE = (
        ('Connexion', 'Connexion'),
        ('Adhesion', 'Adhesion'),
        ('All', 'All'),
    )

    facture = models.ForeignKey('Facture', on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(1)])
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.PositiveIntegerField(
        help_text="Durée exprimée en mois entiers",
        blank=True,
        null=True)
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        blank=True,
        null=True,
        max_length=255
    )

    def prix_total(self):
        """Renvoie le prix_total de self (nombre*prix)"""
        return self.prix*self.number

    def update_cotisation(self):
        """Mets à jour l'objet related cotisation de la vente, si
        il existe : update la date de fin à partir de la durée de
        la vente"""
        if hasattr(self, 'cotisation'):
            cotisation = self.cotisation
            cotisation.date_end = cotisation.date_start + relativedelta(
                months=self.duration*self.number)
        return

    def create_cotis(self, date_start=False):
        """Update et crée l'objet cotisation associé à une facture, prend
        en argument l'user, la facture pour la quantitéi, et l'article pour
        la durée"""
        if not hasattr(self, 'cotisation') and self.type_cotisation:
            cotisation = Cotisation(vente=self)
            cotisation.type_cotisation = self.type_cotisation
            if date_start:
                end_adhesion = Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.filter(
                            user=self.facture.user
                        ).exclude(valid=False))
                    ).filter(Q(type_cotisation='All') | Q(type_cotisation=self.type_cotisation)
                    ).filter(
                        date_start__lt=date_start
                    ).aggregate(Max('date_end'))['date_end__max']
            elif self.type_cotisation=="Adhesion":
                end_cotisation = self.facture.user.end_adhesion()
            else:
                end_cotisation = self.facture.user.end_connexion()
            date_start = date_start or timezone.now()
            end_cotisation = end_cotisation or date_start
            date_max = max(end_cotisation, date_start)
            cotisation.date_start = date_max
            cotisation.date_end = cotisation.date_start + relativedelta(
                months=self.duration*self.number
                )
        return

    def save(self, *args, **kwargs):
        # On verifie que si iscotisation, duration est présent
        if self.type_cotisation and not self.duration:
            raise ValidationError("Cotisation et durée doivent être présents\
                    ensembles")
        self.update_cotisation()
        super(Vente, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)


@receiver(post_save, sender=Vente)
def vente_post_save(sender, **kwargs):
    """Post save d'une vente, déclencge la création de l'objet cotisation
    si il y a lieu(si iscotisation) """
    vente = kwargs['instance']
    if hasattr(vente, 'cotisation'):
        vente.cotisation.vente = vente
        vente.cotisation.save()
    if vente.type_cotisation:
        vente.create_cotis()
        vente.cotisation.save()
        user = vente.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


@receiver(post_delete, sender=Vente)
def vente_post_delete(sender, **kwargs):
    """Après suppression d'une vente, on synchronise l'user ldap (ex
    suppression d'une cotisation"""
    vente = kwargs['instance']
    if vente.type_cotisation:
        user = vente.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


class Article(models.Model):
    """Liste des articles en vente : prix, nom, et attribut iscotisation
    et duree si c'est une cotisation"""
    PRETTY_NAME = "Articles en vente"

    USER_TYPES = (
        ('Adherent', 'Adherent'),
        ('Club', 'Club'),
        ('All', 'All'),
    )

    COTISATION_TYPE = (
        ('Connexion', 'Connexion'),
        ('Adhesion', 'Adhesion'),
        ('All', 'All'),
    )

    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.PositiveIntegerField(
        help_text="Durée exprimée en mois entiers",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    type_user = models.CharField(
        choices=USER_TYPES,
        default='All',
        max_length=255
    )
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        default=None,
        blank=True,
        null=True,
        max_length=255
    )

    unique_together = ('name', 'type_user')

    def clean(self):
        if self.name.lower() == "solde":
            raise ValidationError("Solde est un nom d'article invalide")
        if self.type_cotisation and not self.duration:
            raise ValidationError(
                "La durée est obligatoire si il s'agit d'une cotisation"
            )

    def __str__(self):
        return self.name


class Banque(models.Model):
    """Liste des banques"""
    PRETTY_NAME = "Banques enregistrées"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Paiement(models.Model):
    """Moyens de paiement"""
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
        """Un seul type de paiement peut-etre cheque..."""
        if Paiement.objects.filter(type_paiement=1).count() > 1:
            raise ValidationError("On ne peut avoir plusieurs mode de paiement\
                    chèque")
        super(Paiement, self).save(*args, **kwargs)


class Cotisation(models.Model):
    """Objet cotisation, debut et fin, relié en onetoone à une vente"""
    PRETTY_NAME = "Cotisations"

    COTISATION_TYPE = (
        ('Connexion', 'Connexion'),
        ('Adhesion', 'Adhesion'),
        ('All', 'All'),
    )

    vente = models.OneToOneField('Vente', on_delete=models.CASCADE, null=True)
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        max_length=255,
    )
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return str(self.vente)


@receiver(post_save, sender=Cotisation)
def cotisation_post_save(sender, **kwargs):
    """Après modification d'une cotisation, regeneration des services"""
    regen('dns')
    regen('dhcp')
    regen('mac_ip_list')
    regen('mailing')


@receiver(post_delete, sender=Cotisation)
def vente_post_delete(sender, **kwargs):
    """Après suppression d'une vente, régénération des services"""
    cotisation = kwargs['instance']
    regen('mac_ip_list')
    regen('mailing')
