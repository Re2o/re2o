# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from preferences.models import OptionalUser
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from .models import Article, Paiement, Facture, Banque


class NewFactureForm(FormRevMixin, ModelForm):
    """
    Form used to create a new invoice by using a payment method, a bank and a
    cheque number.
    """
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        allowed_payment = kwargs.pop('allowed_payment', None)
        super(NewFactureForm, self).__init__(*args, prefix=prefix, **kwargs)
        # TODO : remove the use of cheque and banque and paiement
        #        for something more generic or at least in English
        if allowed_payment:
            self.fields['paiement'].queryset = allowed_payment
        self.fields['paiement'].empty_label = \
            _("Select a payment method")

    class Meta:
        model = Facture
        fields = ['paiement']

    def clean(self):
        cleaned_data = super(NewFactureForm, self).clean()
        paiement = cleaned_data.get('paiement')
        cheque = cleaned_data.get('cheque')
        banque = cleaned_data.get('banque')
        if not paiement:
            raise forms.ValidationError(
                _("A payment method must be specified.")
            )
        elif paiement.type_paiement == 'check' and not (cheque and banque):
            raise forms.ValidationError(
                _("A cheque number and a bank must be specified.")
            )
        return cleaned_data


class CreditSoldeForm(NewFactureForm):
    """
    Form used to make some operations on the user's balance if the option is
    activated.
    """
    class Meta(NewFactureForm.Meta):
        model = Facture
        fields = ['paiement', 'banque', 'cheque']

    def __init__(self, *args, **kwargs):
        super(CreditSoldeForm, self).__init__(*args, **kwargs)
        # TODO : change solde to balance
        self.fields['paiement'].queryset = Paiement.objects.exclude(
            moyen='solde'
        ).exclude(moyen='Solde')

    montant = forms.DecimalField(max_digits=5, decimal_places=2, required=True)


class SelectUserArticleForm(
        FormRevMixin, Form):
    """
    Form used to select an article during the creation of an invoice for a
    member.
    """
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(
            Q(type_user='All') | Q(type_user='Adherent')
        ),
        label=_l("Article"),
        required=True
    )
    quantity = forms.IntegerField(
        label=_l("Quantity"),
        validators=[MinValueValidator(1)],
        required=True
    )

    def __init__(self, *args, **kwargs):
        self_subscription = kwargs.pop('is_self_subscription', False)
        super(SelectUserArticleForm, self).__init__(*args, **kwargs)
        if self_subscription:
            self.fields['article'].queryset = Article.objects.filter(
                Q(type_user='All') | Q(type_user='Adherent')
            ).filter(allow_self_subscription=True)


class SelectClubArticleForm(Form):
    """
    Form used to select an article during the creation of an invoice for a
    club.
    """
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(
            Q(type_user='All') | Q(type_user='Club')
        ),
        label=_l("Article"),
        required=True
    )
    quantity = forms.IntegerField(
        label=_l("Quantity"),
        validators=[MinValueValidator(1)],
        required=True
    )

    def __init__(self, *args, **kwargs):
        self_subscription = kwargs.pop('is_self_subscription', False)
        super(SelectClubArticleForm, self).__init__(*args, **kwargs)
        if self_subscription:
            self.fields['article'].queryset = Article.objects.filter(
                Q(type_user='All') | Q(type_user='Club')
            ).filter(allow_self_subscription=True)


# TODO : change Facture to Invoice
class NewFactureFormPdf(Form):
    """
    Form used to create a custom PDF invoice.
    """
    paid = forms.BooleanField(label=_l("Paid"), required=False)
    # TODO : change dest field to recipient
    dest = forms.CharField(
        required=True,
        max_length=255,
        label=_l("Recipient")
    )
    # TODO : change chambre field to address
    chambre = forms.CharField(
        required=False,
        max_length=10,
        label=_l("Address")
    )


# TODO : change Facture to Invoice
class EditFactureForm(FieldPermissionFormMixin, NewFactureForm):
    """
    Form used to edit an invoice and its fields : payment method, bank,
    user associated, ...
    """
    class Meta(NewFactureForm.Meta):
        # TODO : change Facture to Invoice
        model = Facture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # TODO : change Facture to Invoice
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = _("Member")
        self.fields['user'].empty_label = \
            _("Select the proprietary member")
        self.fields['valid'].label = _("Validated invoice")


class ArticleForm(FormRevMixin, ModelForm):
    """
    Form used to create an article.
    """
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ArticleForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Article name")


class DelArticleForm(FormRevMixin, Form):
    """
    Form used to delete one or more of the currently available articles.
    The user must choose the one to delete by checking the boxes.
    """
    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.none(),
        label=_l("Existing articles"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelArticleForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['articles'].queryset = instances
        else:
            self.fields['articles'].queryset = Article.objects.all()


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
        fields = ['moyen', 'allow_self_subscription']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PaiementForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['moyen'].label = _("Payment method name")


# TODO : change paiement to payment
class DelPaiementForm(FormRevMixin, Form):
    """
    Form used to delete one or more payment methods.
    The user must choose the one to delete by checking the boxes.
    """
    # TODO : change paiement to payment
    paiements = forms.ModelMultipleChoiceField(
        queryset=Paiement.objects.none(),
        label=_l("Existing payment method"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelPaiementForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['paiements'].queryset = instances
        else:
            self.fields['paiements'].queryset = Paiement.objects.all()


# TODO : change banque to bank
class BanqueForm(FormRevMixin, ModelForm):
    """
    Form used to create a bank.
    """
    class Meta:
        # TODO : change banque to bank
        model = Banque
        fields = ['name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(BanqueForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Bank name")


# TODO : change banque to bank
class DelBanqueForm(FormRevMixin, Form):
    """
    Form used to delete one or more banks.
    The use must choose the one to delete by checking the boxes.
    """
    # TODO : change banque to bank
    banques = forms.ModelMultipleChoiceField(
        queryset=Banque.objects.none(),
        label=_l("Existing banks"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelBanqueForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['banques'].queryset = instances
        else:
            self.fields['banques'].queryset = Banque.objects.all()


# TODO : change facture to Invoice
class NewFactureSoldeForm(NewFactureForm):
    """
    Form used to create an invoice
    """
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NewFactureSoldeForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = _('Cheque number')
        self.fields['banque'].empty_label = _("Not specified")
        self.fields['paiement'].empty_label = \
            _("Select a payment method")
        # TODO : change paiement to payment
        paiement_list = Paiement.objects.filter(type_paiement=1)
        if paiement_list:
            self.fields['paiement'].widget\
                .attrs['data-cheque'] = paiement_list.first().id

    class Meta:
        # TODO : change facture to invoice
        model = Facture
        # TODO : change paiement to payment and baque to bank
        fields = ['paiement', 'banque']

    def clean(self):
        cleaned_data = super(NewFactureSoldeForm, self).clean()
        # TODO : change paiement to payment
        paiement = cleaned_data.get("paiement")
        cheque = cleaned_data.get("cheque")
        # TODO : change banque to bank
        banque = cleaned_data.get("banque")
        # TODO : change paiement to payment
        if not paiement:
            raise forms.ValidationError(
                _("A payment method must be specified.")
            )
        # TODO : change paiement and banque to payment and bank
        elif paiement.type_paiement == "check" and not (cheque and banque):
            raise forms.ValidationError(
                _("A cheque number and a bank must be specified.")
            )
        return cleaned_data


# TODO : Better name and docstring
class RechargeForm(FormRevMixin, Form):
    """
    Form used to refill a user's balance
    """
    value = forms.FloatField(
        label=_l("Amount"),
        min_value=0.01,
        validators=[]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(RechargeForm, self).__init__(*args, **kwargs)

    def clean_value(self):
        """
        Returns a cleaned vlaue from the received form by validating
        the value is well inside the possible limits
        """
        value = self.cleaned_data['value']
        if value < OptionalUser.get_cached_value('min_online_payment'):
            raise forms.ValidationError(
                _("Requested amount is too small. Minimum amount possible : \
                %(min_online_amount)s €.") % {
                    'min_online_amount': OptionalUser.get_cached_value(
                        'min_online_payment'
                    )
                }
            )
        if value + self.user.solde > \
                OptionalUser.get_cached_value('max_solde'):
            raise forms.ValidationError(
                _("Requested amount is too high. Your balance can't exceed \
                %(max_online_balance)s €.") % {
                    'max_online_balance': OptionalUser.get_cached_value(
                        'max_solde'
                    )
                }
            )
        return value
