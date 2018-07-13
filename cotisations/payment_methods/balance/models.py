# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l
from django.contrib import messages


from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class BalancePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """
    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='payment_method',
        editable=False
    )
    minimum_balance = models.DecimalField(
        verbose_name=_l("Minimum balance"),
        help_text=_l("The minimal amount of money allowed for the balance"
                     " at the end of a payment. You can specify negative "
                     "amount."
                     ),
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    maximum_balance = models.DecimalField(
        verbose_name=_l("Maximum balance"),
        help_text=_l("The maximal amount of money allowed for the balance."),
        max_digits=5,
        decimal_places=2,
        default=50,
        blank=True,
        null=True,
    )

    def end_payment(self, invoice, request):
        """Changes the user's balance to pay the invoice. If it is not
        possible, shows an error and invalidates the invoice.
        """
        user = invoice.user
        total_price = invoice.prix_total()
        if float(user.solde) - float(total_price) < self.minimum_balance:
            invoice.valid = False
            invoice.save()
            messages.error(
                request,
                _("Your balance is too low for this operation.")
            )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': user.id}
            ))
        return invoice.paiement.end_payment(
            invoice,
            request,
            use_payment_method=False
        )

    def valid_form(self, form):
        """Checks that there is not already a balance payment method."""
        p = Paiement.objects.filter(is_balance=True)
        if len(p) > 0:
            form.add_error(
                'payment_method',
                _("There is already a payment type for user balance")
            )

    def alter_payment(self, payment):
        """Register the payment as a balance payment."""
        self.payment.is_balance = True

    def check_invoice(self, invoice_form):
        """Checks that a invoice meets the requirement to be paid with user
        balance.

        Args:
            invoice_form: The invoice_form which is to be checked.

        Returns:
            True if the form is valid for this payment.

        """
        user = invoice_form.instance.user
        total_price = invoice_form.instance.prix_total()
        if float(user.solde) - float(total_price) < self.minimum_balance:
            invoice_form.add_error(
                'paiement',
                _("Your balance is too low for this operation.")
            )
            return False
        return True
