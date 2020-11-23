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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class ChequePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """

    class Meta:
        verbose_name = _("cheque")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name="payment_method_cheque",
        editable=False,
    )

    def end_payment(self, invoice, request):
        """Invalidates the invoice then redirect the user towards a view asking
        for informations to add to the invoice before validating it.
        """
        return redirect(
            reverse("cotisations:cheque:validate", kwargs={"invoice_pk": invoice.pk})
        )
