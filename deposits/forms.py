# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Jean-Romain Garnier
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
Deposit form
"""

from django import forms
from django.forms import Form, ModelForm
from django.utils.translation import ugettext_lazy as _

from re2o.mixins import FormRevMixin

from .models import Deposit, DepositItem


class DepositForm(FormRevMixin, ModelForm):
    """
    Form used to manage and create an invoice and its fields.
    """

    def __init__(self, *args, creation=False, **kwargs):
        user = kwargs.pop("user")
        super(DepositForm, self).__init__(*args, **kwargs)

        if creation:
            # During creation, we only need to select the item and payment
            # method, no need to add the "returned" checkbox
            self.fields = {
                "item": self.fields["item"],
                "payment_method": self.fields["payment_method"],
            }
        else:
            self.fields["returned"].label = _("Deposit returned")

    class Meta:
        model = Deposit
        fields = ("item", "payment_method", "returned")


class DepositItemForm(FormRevMixin, ModelForm):
    """
    Form used to create a deposit item.
    """

    class Meta:
        model = DepositItem
        fields = "__all__"


class DelDepositItemForm(FormRevMixin, Form):
    """
    Form used to delete one or more of the currently available deposit items.
    The user must choose the one to delete by checking the boxes.
    """

    deposit_items = forms.ModelMultipleChoiceField(
        queryset=DepositItem.objects.none(),
        label=_("Current deposit items"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelDepositItemForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["deposit_items"].queryset = instances
        else:
            self.fields["deposit_items"].queryset = DepositItem.objects.all()
