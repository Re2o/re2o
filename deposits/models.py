# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Arthur Grisel-Davy
# Copyright © 2020  Gabriel Détraz
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
Deposit model
"""

from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from re2o.mixins import AclMixin, RevMixin


class Deposit(RevMixin, AclMixin, models.Model):
    """
    The model for a deposit. It reprensents the fact that a user made a deposit
    as a guarantee for an item which should be returned to get the deposit
    back.

    A deposit is linked to :
        * a user (the one who made the deposit)
        * an item (borrowed in exchange for the deposit)
    Every deposit is dated throught the 'date' value. Its amount is saved in
    the 'deposit_amount' in case an item's amount changes later on.
    A deposit has a 'returned' value (default: False) which means that the item
    was returned by the user and the deposit was payed back.
    """

    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    item = models.ForeignKey("DepositItem", on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("date"))
    returned = models.BooleanField(default=False, verbose_name=_("returned"))
    deposit_amount = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("deposit amount")
    )

    class Meta:
        abstract = False
        verbose_name = _("deposit")
        verbose_name_plural = _("deposits")

    def __init__(self, *args, **kwargs):
        super(Deposit, self).__init__(*args, **kwargs)
        self.__original_item = self.item
        self.__original_deposit_amount = self.deposit_amount

    def __str__(self):
        if self.returned:
            return _("Deposit from {name} for {item} at {date}, returned").format(
                name=self.user.get_full_name(),
                item=self.item,
                date=self.date,
            )
        else:
            return _(
                "Deposit from {name} for {item} at {date}, not yet returned"
            ).format(
                name=self.user.get_full_name(),
                item=self.item,
                date=self.date,
            )

    def save(self, *args, **kwargs):
        # Save the item's deposit amount in the deposit's attribute
        self.deposit_amount = self.item.deposit_amount

        # If the item didn't change, keep the previous deposit_amount
        # This is done in case a DepositItem's deposit_amount is changed, we
        # want to make sure deposits created before keep the same amount
        if self.__original_deposit_amount and self.item == self.__original_item:
            self.deposit_amount = self.__original_deposit_amount

        super(Deposit, self).save(*args, **kwargs)

    def can_view(self, user_request, *_args, **_kwargs):
        """Check that the user has the right to view the deposit or that it
        belongs to them."""
        if (
            not user_request.has_perm("deposits.view_deposit")
            and self.user != user_request
        ):
            return (
                False,
                _("You don't have the right to view other deposits than yours."),
                ("deposits.view_deposit",),
            )
        else:
            return True, None, None

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check that the user has access to the list of all tickets."""
        can = user_request.has_perm("deposits.view_deposit")
        return (
            can,
            _("You don't have the right to view the list of deposits.")
            if not can
            else None,
            ("deposits.view_deposit",),
        )


class DepositItem(RevMixin, AclMixin, models.Model):
    """An item for a deposit.

    Attributes:
        name: the name of this deposit item.
        deposit_amount: the amount needed to be deposited by users.
    """

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        verbose_name=_("designation"),
    )
    deposit_amount = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("deposit amount")
    )

    class Meta:
        abstract = False
        verbose_name = _("deposit item")
        verbose_name_plural = _("deposit items")

    def __str__(self):
        return self.name
