# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Hugo Levy-Falk
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
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class FreePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to bypass payment if the invoice is free.
    """

    class Meta:
        verbose_name = _("Free payment")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name="payment_method_free",
        editable=False,
    )

    def end_payment(self, invoice, request, *args, **kwargs):
        """Ends the payment normally.
        """
        return invoice.paiement.end_payment(invoice, request, use_payment_method=False)

    def check_price(self, price, user, *args, **kwargs):
        """Checks that the price meets the requirement to be paid with user
        balance.
        """
        return (price == 0, _("You can't pay this invoice for free."))
