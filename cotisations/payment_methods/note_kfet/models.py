# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Pierre-Antoine Comby
# Copyright © 2018  Gabriel Detraz
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
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin

from django.shortcuts import render, redirect


class NotePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with NoteKfet2015.
    """

    class Meta:
        verbose_name = _("NoteKfet")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name="payment_method_note",
        editable=False,
    )
    server = models.CharField(max_length=255, verbose_name=_("server"))
    port = models.PositiveIntegerField(blank=True, null=True)
    id_note = models.PositiveIntegerField(blank=True, null=True)

    def end_payment(self, invoice, request):
        return redirect(
            reverse(
                "cotisations:note_kfet:note_payment", kwargs={"factureid": invoice.id}
            )
        )
