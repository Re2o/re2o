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
The database models for the 'cotisation' app of re2o.
The goal is to keep the main actions here, i.e. the 'clean' and 'save'
function are higly reposnsible for the changes, checking the coherence of the
data and the good behaviour in general for not breaking the database.

For further details on each of those models, see the documentation details for
each.
"""

from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Q, Max
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from machines.models import regen
from re2o.field_permissions import FieldPermissionModelMixin
from re2o.mixins import AclMixin, RevMixin


# TODO : change facture to invoice
class Facture(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    """
    The model for an invoice. It reprensents the fact that a user paid for
    something (it can be multiple article paid at once).

    An invoice is linked to :
        * one or more purchases (one for each article sold that time)
        * a user (the one who bought those articles)
        * a payment method (the one used by the user)
        * (if applicable) a bank
        * (if applicable) a cheque number.
    Every invoice is dated throught the 'date' value.
    An invoice has a 'controlled' value (default : False) which means that
    someone with high enough rights has controlled that invoice and taken it
    into account. It also has a 'valid' value (default : True) which means
    that someone with high enough rights has decided that this invoice was not
    valid (thus it's like the user never paid for his articles). It may be
    necessary in case of non-payment.
    """

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    # TODO : change paiement to payment
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    # TODO : change banque to bank
    banque = models.ForeignKey(
        'Banque',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    # TODO : maybe change to cheque nummber because not evident
    cheque = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_l("Cheque number")
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_l("Date")
    )
    # TODO : change name to validity for clarity
    valid = models.BooleanField(
        default=True,
        verbose_name=_l("Validated")
    )
    # TODO : changed name to controlled for clarity
    control = models.BooleanField(
        default=False,
        verbose_name=_l("Controlled")
    )

    class Meta:
        abstract = False
        permissions = (
            # TODO : change facture to invoice
            ('change_facture_control',
             _l("Can change the \"controlled\" state")),
            # TODO : seems more likely to be call create_facture_pdf
            # or create_invoice_pdf
            ('change_facture_pdf',
             _l("Can create a custom PDF invoice")),
            ('view_facture',
             _l("Can see an invoice's details")),
            ('change_all_facture',
             _l("Can edit all the previous invoices")),
        )
        verbose_name = _l("Invoice")
        verbose_name_plural = _l("Invoices")

    def linked_objects(self):
        """Return linked objects : machine and domain.
        Usefull in history display"""
        return self.vente_set.all()

    # TODO : change prix to price
    def prix(self):
        """
        Returns: the raw price without the quantities.
        Deprecated, use :total_price instead.
        """
        price = Vente.objects.filter(
            facture=self
            ).aggregate(models.Sum('prix'))['prix__sum']
        return price

    # TODO : change prix to price
    def prix_total(self):
        """
        Returns: the total price for an invoice. Sum all the articles' prices
        and take the quantities into account.
        """
        # TODO : change Vente to somethingelse
        return Vente.objects.filter(
            facture=self
            ).aggregate(
                total=models.Sum(
                    models.F('prix')*models.F('number'),
                    output_field=models.FloatField()
                )
            )['total']

    def name(self):
        """
        Returns : a string with the name of all the articles in the invoice.
        Used for reprensenting the invoice with a string.
        """
        name = ' - '.join(Vente.objects.filter(
            facture=self
            ).values_list('name', flat=True))
        return name

    def can_edit(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.change_facture'):
            return False, _("You don't have the right to edit an invoice.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                not self.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to edit this user's "
                            "invoices.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                (self.control or not self.valid):
            return False, _("You don't have the right to edit an invoice "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.delete_facture'):
            return False, _("You don't have the right to delete an invoice.")
        if not self.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to delete this user's "
                            "invoices.")
        if self.control or not self.valid:
            return False, _("You don't have the right to delete an invoice "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.view_facture') and \
                self.user != user_request:
            return False, _("You don't have the right to see someone else's "
                            "invoices history.")
        elif not self.valid:
            return False, _("The invoice has been invalidated.")
        else:
            return True, None

    @staticmethod
    def can_change_control(user_request, *_args, **_kwargs):
        """ Returns True if the user can change the 'controlled' status of
        this invoice """
        return (
            user_request.has_perm('cotisations.change_facture_control'),
            _("You don't have the right to edit the \"controlled\" state.")
        )

    @staticmethod
    def can_change_pdf(user_request, *_args, **_kwargs):
        """ Returns True if the user can change this invoice """
        return (
            user_request.has_perm('cotisations.change_facture_pdf'),
            _("You don't have the right to edit an invoice.")
        )

    def __init__(self, *args, **kwargs):
        super(Facture, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'control': self.can_change_control,
        }

    def __str__(self):
        return str(self.user) + ' ' + str(self.date)


@receiver(post_save, sender=Facture)
def facture_post_save(_sender, **kwargs):
    """
    Synchronise the LDAP user after an invoice has been saved.
    """
    facture = kwargs['instance']
    user = facture.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


@receiver(post_delete, sender=Facture)
def facture_post_delete(_sender, **kwargs):
    """
    Synchronise the LDAP user after an invoice has been deleted.
    """
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


# TODO : change Vente to Purchase
class Vente(RevMixin, AclMixin, models.Model):
    """
    The model defining a purchase. It consist of one type of article being
    sold. In particular there may be multiple purchases in a single invoice.

    It's reprensentated by:
        * an amount (the number of items sold)
        * an invoice (whose the purchase is part of)
        * an article
        * (if applicable) a cotisation (which holds some informations about
            the effect of the purchase on the time agreed for this user)
    """

    # TODO : change this to English
    COTISATION_TYPE = (
        ('Connexion', _l("Connexion")),
        ('Adhesion', _l("Membership")),
        ('All', _l("Both of them")),
    )

    # TODO : change facture to invoice
    facture = models.ForeignKey(
        'Facture',
        on_delete=models.CASCADE,
        verbose_name=_l("Invoice")
    )
    # TODO : change number to amount for clarity
    number = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_l("Amount")
    )
    # TODO : change this field for a ForeinKey to Article
    name = models.CharField(
        max_length=255,
        verbose_name=_l("Article")
    )
    # TODO : change prix to price
    # TODO : this field is not needed if you use Article ForeignKey
    prix = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_l("Price"))
    # TODO : this field is not needed if you use Article ForeignKey
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_l("Duration (in whole month)")
    )
    # TODO : this field is not needed if you use Article ForeignKey
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_l("Type of cotisation")
    )

    class Meta:
        permissions = (
            ('view_vente', _l("Can see a purchase's details")),
            ('change_all_vente', _l("Can edit all the previous purchases")),
        )
        verbose_name = _l("Purchase")
        verbose_name_plural = _l("Purchases")

    # TODO : change prix_total to total_price
    def prix_total(self):
        """
        Returns: the total of price for this amount of items.
        """
        return self.prix*self.number

    def update_cotisation(self):
        """
        Update the related object 'cotisation' if there is one. Based on the
        duration of the purchase.
        """
        if hasattr(self, 'cotisation'):
            cotisation = self.cotisation
            cotisation.date_end = cotisation.date_start + relativedelta(
                months=self.duration*self.number)
        return

    def create_cotis(self, date_start=False):
        """
        Update and create a 'cotisation' related object if there is a
        cotisation_type defined (which means the article sold represents
        a cotisation)
        """
        if not hasattr(self, 'cotisation') and self.type_cotisation:
            cotisation = Cotisation(vente=self)
            cotisation.type_cotisation = self.type_cotisation
            if date_start:
                end_cotisation = Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.filter(
                            user=self.facture.user
                        ).exclude(valid=False))
                    ).filter(
                        Q(type_cotisation='All') |
                        Q(type_cotisation=self.type_cotisation)
                    ).filter(
                        date_start__lt=date_start
                    ).aggregate(Max('date_end'))['date_end__max']
            elif self.type_cotisation == "Adhesion":
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
        """
        Save a purchase object and check if all the fields are coherents
        It also update the associated cotisation in the changes have some
        effect on the user's cotisation
        """
        # Checking that if a cotisation is specified, there is also a duration
        if self.type_cotisation and not self.duration:
            raise ValidationError(
                _("A cotisation should always have a duration.")
            )
        self.update_cotisation()
        super(Vente, self).save(*args, **kwargs)

    def can_edit(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.change_vente'):
            return False, _("You don't have the right to edit the purchases.")
        elif (not user_request.has_perm('cotisations.change_all_facture') and
              not self.facture.user.can_edit(
                  user_request, *args, **kwargs
              )[0]):
            return False, _("You don't have the right to edit this user's "
                            "purchases.")
        elif (not user_request.has_perm('cotisations.change_all_vente') and
              (self.facture.control or not self.facture.valid)):
            return False, _("You don't have the right to edit a purchase "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.delete_vente'):
            return False, _("You don't have the right to delete a purchase.")
        if not self.facture.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to delete this user's "
                            "purchases.")
        if self.facture.control or not self.facture.valid:
            return False, _("You don't have the right to delete a purchase "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if (not user_request.has_perm('cotisations.view_vente') and
                self.facture.user != user_request):
            return False, _("You don't have the right to see someone "
                            "else's purchase history.")
        else:
            return True, None

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)


# TODO : change vente to purchase
@receiver(post_save, sender=Vente)
def vente_post_save(_sender, **kwargs):
    """
    Creates a 'cotisation' related object if needed and synchronise the
    LDAP user when a purchase has been saved.
    """
    purchase = kwargs['instance']
    if hasattr(purchase, 'cotisation'):
        purchase.cotisation.vente = purchase
        purchase.cotisation.save()
    if purchase.type_cotisation:
        purchase.create_cotis()
        purchase.cotisation.save()
        user = purchase.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


# TODO : change vente to purchase
@receiver(post_delete, sender=Vente)
def vente_post_delete(_sender, **kwargs):
    """
    Synchronise the LDAP user after a purchase has been deleted.
    """
    purchase = kwargs['instance']
    if purchase.type_cotisation:
        user = purchase.facture.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


class Article(RevMixin, AclMixin, models.Model):
    """
    The definition of an article model. It represents a type of object
    that can be sold to the user.

    It's represented by:
        * a name
        * a price
        * a cotisation type (indicating if this article reprensents a
            cotisation or not)
        * a duration (if it is a cotisation)
        * a type of user (indicating what kind of user can buy this article)
    """

    # TODO : Either use TYPE or TYPES in both choices but not both
    USER_TYPES = (
        ('Adherent', _l("Member")),
        ('Club', _l("Club")),
        ('All', _l("Both of them")),
    )

    COTISATION_TYPE = (
        ('Connexion', _l("Connexion")),
        ('Adhesion', _l("Membership")),
        ('All', _l("Both of them")),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_l("Designation")
    )
    # TODO : change prix to price
    prix = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_l("Unitary price")
    )
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_l("Duration (in whole month)")
    )
    type_user = models.CharField(
        choices=USER_TYPES,
        default='All',
        max_length=255,
        verbose_name=_l("Type of users concerned")
    )
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        default=None,
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_l("Type of cotisation")
    )

    unique_together = ('name', 'type_user')

    class Meta:
        permissions = (
            ('view_article', _l("Can see an article's details")),
        )
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def clean(self):
        if self.name.lower() == 'solde':
            raise ValidationError(
                _("Solde is a reserved article name")
            )
        if self.type_cotisation and not self.duration:
            raise ValidationError(
                _("Duration must be specified for a cotisation")
            )

    def __str__(self):
        return self.name


class Banque(RevMixin, AclMixin, models.Model):
    """
    The model defining a bank. It represents a user's bank. It's mainly used
    for statistics by regrouping the user under their bank's name and avoid
    the use of a simple name which leads (by experience) to duplicates that
    only differs by a capital letter, a space, a misspelling, ... That's why
    it's easier to use simple object for the banks.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_l("Name")
    )

    class Meta:
        permissions = (
            ('view_banque', _l("Can see a bank's details")),
        )
        verbose_name = _l("Bank")
        verbose_name_plural = _l("Banks")

    def __str__(self):
        return self.name


# TODO : change Paiement to Payment
class Paiement(RevMixin, AclMixin, models.Model):
    """
    The model defining a payment method. It is how the user is paying for the
    invoice. It's easier to know this information when doing the accouts.
    It is represented by:
        * a name
        * a type (used for the type 'cheque' which implies the use of a bank
            and an account number in related models)
    """

    PAYMENT_TYPES = (
        (0, _l("Standard")),
        (1, _l("Cheque")),
    )

    # TODO : change moyen to method
    moyen = models.CharField(
        max_length=255,
        verbose_name=_l("Method")
    )
    type_paiement = models.IntegerField(
        choices=PAYMENT_TYPES,
        default=0,
        verbose_name=_l("Payment type")
    )

    class Meta:
        permissions = (
            ('view_paiement', _l("Can see a payement's details")),
        )
        verbose_name = _l("Payment method")
        verbose_name_plural = _l("Payment methods")

    def __str__(self):
        return self.moyen

    def clean(self):
        """
        Override of the herited clean function to get a correct name
        """
        self.moyen = self.moyen.title()

    def save(self, *args, **kwargs):
        """
        Override of the herited save function to be sure only one payment
        method of type 'cheque' exists.
        """
        if Paiement.objects.filter(type_paiement=1).count() > 1:
            raise ValidationError(
                _("You cannot have multiple payment method of type cheque")
            )
        super(Paiement, self).save(*args, **kwargs)


class Cotisation(RevMixin, AclMixin, models.Model):
    """
    The model defining a cotisation. It holds information about the time a user
    is allowed when he has paid something.
    It characterised by :
        * a date_start (the date when the cotisaiton begins/began
        * a date_end (the date when the cotisation ends/ended
        * a type of cotisation (which indicates the implication of such
            cotisation)
        * a purchase (the related objects this cotisation is linked to)
    """

    COTISATION_TYPE = (
        ('Connexion', _l("Connexion")),
        ('Adhesion', _l("Membership")),
        ('All', _l("Both of them")),
    )

    # TODO : change vente to purchase
    vente = models.OneToOneField(
        'Vente',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_l("Purchase")
    )
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        max_length=255,
        default='All',
        verbose_name=_l("Type of cotisation")
    )
    date_start = models.DateTimeField(
        verbose_name=_l("Starting date")
    )
    date_end = models.DateTimeField(
        verbose_name=_l("Ending date")
    )

    class Meta:
        permissions = (
            ('view_cotisation', _l("Can see a cotisation's details")),
            ('change_all_cotisation', _l("Can edit the previous cotisations")),
        )

    def can_edit(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.change_cotisation'):
            return False, _("You don't have the right to edit a cotisation.")
        elif not user_request.has_perm('cotisations.change_all_cotisation') \
                and (self.vente.facture.control or
                     not self.vente.facture.valid):
            return False, _("You don't have the right to edit a cotisation "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.delete_cotisation'):
            return False, _("You don't have the right to delete a "
                            "cotisation.")
        if self.vente.facture.control or not self.vente.facture.valid:
            return False, _("You don't have the right to delete a cotisation "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.view_cotisation') and\
                self.vente.facture.user != user_request:
            return False, _("You don't have the right to see someone else's "
                            "cotisation history.")
        else:
            return True, None

    def __str__(self):
        return str(self.vente)


@receiver(post_save, sender=Cotisation)
def cotisation_post_save(_sender, **_kwargs):
    """
    Mark some services as needing a regeneration after the edition of a
    cotisation. Indeed the membership status may have changed.
    """
    regen('dns')
    regen('dhcp')
    regen('mac_ip_list')
    regen('mailing')


@receiver(post_delete, sender=Cotisation)
def cotisation_post_delete(_sender, **_kwargs):
    """
    Mark some services as needing a regeneration after the deletion of a
    cotisation. Indeed the membership status may have changed.
    """
    regen('mac_ip_list')
    regen('mailing')
