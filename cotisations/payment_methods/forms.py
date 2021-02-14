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
from django import forms
from django.utils.translation import ugettext_lazy as _

from cotisations.utils import find_payment_method

from . import PAYMENT_METHODS


def payment_method_factory(payment, *args, creation=True, **kwargs):
    """This function finds the right payment method form for a given payment.

    If the payment has a payment method, returns a ModelForm of it. Else if
    it is the creation of the payment, a `PaymentMethodForm`.
    Else `None`.

    Args:
        payment: The payment
        *args: arguments passed to the form
        creation: Should be True if you are creating the payment
        **kwargs: passed to the form

    Returns:
        A form or None
    """
    payment_method = kwargs.pop("instance", find_payment_method(payment))
    if payment_method is not None:
        return forms.modelform_factory(type(payment_method), fields="__all__")(
            *args, instance=payment_method, **kwargs
        )
    elif creation:
        return PaymentMethodForm(*args, **kwargs)


class PaymentMethodForm(forms.Form):
    """A special form which allows you to add a payment method to a `Payment`
    object.
    """

    payment_method = forms.ChoiceField(
        label=_("Special payment method"),
        help_text=_(
            "Warning: you will not be able to change the payment"
            " method later. But you will be allowed to edit the other"
            " options."
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        prefix = kwargs.get("prefix", None)
        self.fields["payment_method"].choices = [
            (i, p.NAME) for (i, p) in enumerate(PAYMENT_METHODS)
        ]
        self.fields["payment_method"].choices.insert(0, ("", _("No")))
        self.fields["payment_method"].widget.attrs = {"id": "paymentMethodSelect"}
        self.templates = [
            forms.modelform_factory(p.PaymentMethod, fields="__all__")(prefix=prefix)
            for p in PAYMENT_METHODS
        ]

    def clean(self):
        """A classic `clean` method, except that it replaces
        `self.payment_method` by the payment method object if one has been
        found. Tries to call `payment_method.valid_form` if it exists.
        """
        super(PaymentMethodForm, self).clean()
        choice = self.cleaned_data["payment_method"]
        if choice == "":
            return
        choice = int(choice)
        model = PAYMENT_METHODS[choice].PaymentMethod
        form = forms.modelform_factory(model, fields="__all__")(
            self.data, prefix=self.prefix
        )
        self.payment_method = form.save(commit=False)
        if hasattr(self.payment_method, "valid_form"):
            self.payment_method.valid_form(self)
        return self.cleaned_data

    def save(self, payment, *args, **kwargs):
        """Saves the payment method.

        Tries to call `payment_method.alter_payment` if it exists.
        """
        commit = kwargs.pop("commit", True)
        if not hasattr(self, "payment_method"):
            return None
        self.payment_method.payment = payment
        if hasattr(self.payment_method, "alter_payment"):
            self.payment_method.alter_payment(payment)
        if commit:
            payment.save()
            self.payment_method.save()
        return self.payment_method
