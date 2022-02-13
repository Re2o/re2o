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
"""Payment

Here are defined some views dedicated to cheque payement.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from cotisations.models import Facture as Invoice
from cotisations.utils import find_payment_method

from re2o.acl import can_view

from .forms import InvoiceForm
from .models import ChequePayment


@login_required
@can_view(Invoice)
def cheque(request, invoice, **_kwargs):
    """This view validate an invoice with the data from a cheque."""
    payment_method = find_payment_method(invoice.paiement)
    if invoice.valid or not isinstance(payment_method, ChequePayment):
        messages.error(request, _("You can't pay this invoice with a cheque."))
        return redirect(reverse("users:profil", kwargs={"userid": request.user.pk}))
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.instance.valid = True
        # For is saved in call to end_payment
        return form.instance.paiement.end_payment(
            form.instance, request, use_payment_method=False
        )
    return render(
        request,
        "cotisations/payment.html",
        {"form": form, "amount": invoice.prix_total()},
    )
