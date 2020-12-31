# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
# Copyright © 2017  Augustin Lemesle
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
"""
Forms for the 'cotisation' app of re2o. It highly depends on
:cotisations:models and is mainly used by :cotisations:views.

The following forms are mainly used to create, edit or delete
anything related to 'cotisations' :
    * Payments Methods
    * Banks
    * Invoices
    * Articles

See the details for each of these operations in the documentation
of each of the method.
"""
from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.forms import ModelForm, Form
from django.core.validators import MinValueValidator

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import (
    FormRevMixin,
    AutocompleteModelMixin,
    AutocompleteMultipleModelMixin,
)
from .models import (
    Article,
    Paiement,
    Facture,
    Banque,
    CustomInvoice,
    Vente,
    CostEstimate,
)
from .payment_methods import balance


class FactureForm(FieldPermissionFormMixin, FormRevMixin, ModelForm):
    """
    Form used to manage and create an invoice and its fields.
    """

    def __init__(self, *args, creation=False, **kwargs):
        user = kwargs["user"]
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(FactureForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["paiement"].empty_label = _("Select a payment method")
        self.fields["paiement"].queryset = Paiement.find_allowed_payments(user)
        if not creation:
            self.fields["user"].label = _("Member")
            self.fields["user"].empty_label = _("Select the proprietary member")
            self.fields["valid"].label = _("Validated invoice")
        else:
            self.fields = {"paiement": self.fields["paiement"]}

    class Meta:
        model = Facture
        fields = "__all__"
        widgets = {
            "user": AutocompleteModelMixin(url="/users/user-autocomplete"),
            "banque": AutocompleteModelMixin(url="/cotisations/banque-autocomplete"),
        }

    def clean(self):
        cleaned_data = super(FactureForm, self).clean()
        paiement = cleaned_data.get("paiement")
        if not paiement:
            raise forms.ValidationError(_("A payment method must be specified."))
        return cleaned_data


class SelectArticleForm(FormRevMixin, Form):
    """
    Form used to select an article during the creation of an invoice for a
    member.
    """

    article = forms.ModelChoiceField(
        queryset=Article.objects.none(), label=_("Article"), required=True
    )
    quantity = forms.IntegerField(
        label=_("Quantity"), validators=[MinValueValidator(1)], required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        target_user = kwargs.pop("target_user", None)
        super(SelectArticleForm, self).__init__(*args, **kwargs)
        self.fields["article"].queryset = Article.find_allowed_articles(
            user, target_user
        )


class DiscountForm(Form):
    """
    Form used in oder to create a discount on an invoice.
    """

    is_relative = forms.BooleanField(
        label=_("Discount is in percentage."), required=False
    )
    discount = forms.DecimalField(
        label=_("Discount"),
        max_value=100,
        min_value=0,
        max_digits=5,
        decimal_places=2,
        required=False,
    )

    def apply_to_invoice(self, invoice):
        invoice_price = invoice.prix_total()
        discount = self.cleaned_data["discount"]
        is_relative = self.cleaned_data["is_relative"]
        if is_relative:
            amount = discount / 100 * invoice_price
        else:
            amount = discount
        if amount:
            name = _("{}% discount") if is_relative else _("{} € discount")
            name = name.format(discount)
            Vente.objects.create(facture=invoice, name=name, prix=-amount, number=1)


class CustomInvoiceForm(FormRevMixin, ModelForm):
    """
    Form used to create a custom invoice.
    """

    class Meta:
        model = CustomInvoice
        fields = "__all__"


class CostEstimateForm(FormRevMixin, ModelForm):
    """
    Form used to create a cost estimate.
    """

    class Meta:
        model = CostEstimate
        exclude = ["paid", "final_invoice"]


class ArticleForm(FormRevMixin, ModelForm):
    """
    Form used to create an article.
    """

    class Meta:
        model = Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(ArticleForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("Article name")


class DelArticleForm(FormRevMixin, Form):
    """
    Form used to delete one or more of the currently available articles.
    The user must choose the one to delete by checking the boxes.
    """

    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.none(),
        label=_("Current articles"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelArticleForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["articles"].queryset = instances
        else:
            self.fields["articles"].queryset = Article.objects.all()


# TODO : change Paiement to Payment
class PaiementForm(FormRevMixin, ModelForm):
    """
    Form used to create a new payment method.
    The 'cheque' type is used to associate a specific behaviour requiring
    a cheque number and a bank.
    """

    class Meta:
        model = Paiement
        # TODO : change moyen to method and type_paiement to payment_type
        fields = ["moyen", "available_for_everyone"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(PaiementForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["moyen"].label = _("Payment method name")


# TODO : change paiement to payment
class DelPaiementForm(FormRevMixin, Form):
    """
    Form used to delete one or more payment methods.
    The user must choose the one to delete by checking the boxes.
    """

    # TODO : change paiement to payment
    paiements = forms.ModelMultipleChoiceField(
        queryset=Paiement.objects.none(),
        label=_("Current payment methods"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelPaiementForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["paiements"].queryset = instances
        else:
            self.fields["paiements"].queryset = Paiement.objects.all()


# TODO : change banque to bank
class BanqueForm(FormRevMixin, ModelForm):
    """
    Form used to create a bank.
    """

    class Meta:
        # TODO : change banque to bank
        model = Banque
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", self.Meta.model.__name__)
        super(BanqueForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields["name"].label = _("Bank name")


# TODO : change banque to bank
class DelBanqueForm(FormRevMixin, Form):
    """
    Form used to delete one or more banks.
    The use must choose the one to delete by checking the boxes.
    """

    # TODO : change banque to bank
    banques = forms.ModelMultipleChoiceField(
        queryset=Banque.objects.none(),
        label=_("Current banks"),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop("instances", None)
        super(DelBanqueForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields["banques"].queryset = instances
        else:
            self.fields["banques"].queryset = Banque.objects.all()


# TODO : Better name and docstring
class RechargeForm(FormRevMixin, Form):
    """
    Form used to refill a user's balance
    """

    value = forms.DecimalField(label=_("Amount"), decimal_places=2)
    payment = forms.ModelChoiceField(
        queryset=Paiement.objects.none(), label=_("Payment method")
    )

    def __init__(self, *args, user=None, user_source=None, **kwargs):
        self.user = user
        super(RechargeForm, self).__init__(*args, **kwargs)
        self.fields["payment"].empty_label = _("Select a payment method")
        self.fields["payment"].queryset = Paiement.find_allowed_payments(
            user_source
        ).exclude(is_balance=True)

    def clean(self):
        """
        Returns a cleaned value from the received form by validating
        the value is well inside the possible limits
        """
        value = self.cleaned_data["value"]
        balance_method = get_object_or_404(balance.PaymentMethod)
        if (
            balance_method.maximum_balance is not None
            and value + self.user.solde > balance_method.maximum_balance
        ):
            raise forms.ValidationError(
                _(
                    "Requested amount is too high. Your balance can't exceed"
                    " %(max_online_balance)s €."
                )
                % {"max_online_balance": balance_method.maximum_balance}
            )
        return self.cleaned_data
