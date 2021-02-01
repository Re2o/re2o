# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Yohann D'ANELLO
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
This app provides a clean way to make a subscription,
to make a captive portal.

This is only sugar, this does not provide any model.

To use this app, simply install the app into the Django project
(this is completely optional), then configure your reverse proxy
to redirect all requests to /portail/.
The app provides new views to sign in and buy articles, to avoid
accessing to the full Re2o.
"""

from cotisations.models import Facture, Vente
from cotisations.utils import find_payment_method
from django.contrib.auth import login
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from preferences.models import AssoOption

from .forms import AdherentForm, MembershipForm


class SignUpView(CreateView):
    """
    Enable users to sign up and automatically buy a new membership and a connection.
    """
    form_class = AdherentForm
    template_name = "portail/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership_form"] = MembershipForm(self.request.POST or None)
        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        When the registration form is submitted, a new account is created and a membership is bought.
        """
        membership_form = MembershipForm(self.request.POST or None)

        if not membership_form.is_valid():
            return self.form_invalid(form)

        form.save()

        # Login automatically into the new account
        user = form.instance
        login(self.request, form.instance)

        # Buy the new membership
        payment_method = membership_form.cleaned_data["payment_method"]
        article = membership_form.cleaned_data["article"]

        true_payment_method = find_payment_method(payment_method)
        if hasattr(true_payment_method, "check_price"):
            price_ok, msg = true_payment_method.check_price(article.prix, user)
            if not price_ok:
                membership_form.add_error(None, msg)
                return self.form_invalid(membership_form)

        invoice = Facture.objects.create(
            user=user,
            paiement=payment_method,
        )

        Vente.objects.create(
            facture=invoice,
            name=article.name,
            prix=article.prix,
            duration_connection=article.duration_connection,
            duration_days_connection=article.duration_days_connection,
            duration_membership=article.duration_membership,
            duration_days_membership=article.duration_days_membership,
            number=1,
        )

        super().form_valid(form)

        # POOP CODE, pliz Re2o
        # End the payment process, it mays redirect to ComNPay
        return payment_method.end_payment(invoice, self.request)

    def get_success_url(self):
        return reverse_lazy("users:profil", args=(self.object.pk,))


class IndexView(TemplateView):
    """
    Custom index page for the captive portal.
    """
    template_name = "portail/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asso"] = AssoOption.objects.get_or_create()[0]
        return context
