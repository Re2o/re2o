# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Detraz
# Copyright © 2018  Pierre-Antoine Comby
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

Here are the views needed by comnpay
"""

from collections import OrderedDict

from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest

from cotisations.models import Facture
from cotisations.utils import find_payment_method
from .models import NotePayment
from re2o.views import form
from re2o.acl import can_create, can_edit
from .note import login, don
from .forms import NoteCredentialForm


@login_required
@can_edit(Facture)
def note_payment(request, facture, factureid):
    """
    Build a request to start the negociation with NoteKfet by using
    a facture id, the price and the login/password data stored in
    the preferences.
    """
    user = facture.user
    payment_method = find_payment_method(facture.paiement)
    if not payment_method or not isinstance(payment_method, NotePayment):
        messages.error(request, _("Unknown error."))
        return redirect(reverse("users:profil", kwargs={"userid": user.id}))
    noteform = NoteCredentialForm(request.POST or None)
    if noteform.is_valid():
        pseudo = noteform.cleaned_data["login"]
        password = noteform.cleaned_data["password"]
        result, sock, err = login(
            payment_method.server, payment_method.port, pseudo, password
        )
        if not result:
            messages.error(request, err)
            return form(
                {"form": noteform, "amount": facture.prix_total()},
                "cotisations/payment.html",
                request,
            )
        else:
            result, err = don(
                sock, facture.prix_total(), payment_method.id_note, facture
            )
            if not result:
                messages.error(request, err)
                return form(
                    {"form": noteform, "amount": facture.prix_total()},
                    "cotisations/payment.html",
                    request,
                )
        facture.valid = True
        facture.save()
        messages.success(request, _("The payment with note was done."))
        return redirect(reverse("users:profil", kwargs={"userid": user.id}))
    return form(
        {"form": noteform, "amount": facture.prix_total()},
        "cotisations/payment.html",
        request,
    )
