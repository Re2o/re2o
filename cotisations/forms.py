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
Forms de l'application cotisation de re2o. Dépendance avec les models,
importé par les views.

Permet de créer une nouvelle facture pour un user (NewFactureForm),
et de l'editer (soit l'user avec EditFactureForm,
soit le trésorier avec TrezEdit qui a plus de possibilités que self
notamment sur le controle trésorier SelectArticleForm est utilisée
lors de la creation d'une facture en
parrallèle de NewFacture pour le choix des articles désirés.
(la vue correspondante est unique)

ArticleForm, BanqueForm, PaiementForm permettent aux admin d'ajouter,
éditer ou supprimer une banque/moyen de paiement ou un article
"""
from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.forms import ModelForm, Form
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils.translation import ugettext as _

from .models import Article, Paiement, Facture, Banque
from preferences.models import OptionalUser
from users.models import User

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin 

class NewFactureForm(FormRevMixin, ModelForm):
    """Creation d'une facture, moyen de paiement, banque et numero
    de cheque"""
    # TODO : translate doc string in English
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NewFactureForm, self).__init__(*args, prefix=prefix, **kwargs)
        # TODO : remove the use of cheque and banque and paiement
        #        for something more generic or at least in English
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = _("Cheque number")
        self.fields['banque'].empty_label = _("Not specified")
        self.fields['paiement'].empty_label = \
            _("Select a payment method")
        paiement_list = Paiement.objects.filter(type_paiement=1)
        if paiement_list:
            self.fields['paiement'].widget\
                .attrs['data-cheque'] = paiement_list.first().id

    class Meta:
        model = Facture
        fields = ['paiement', 'banque', 'cheque']

    def clean(self):
        cleaned_data = super(NewFactureForm, self).clean()
        paiement = cleaned_data.get('paiement')
        cheque = cleaned_data.get('cheque')
        banque = cleaned_data.get('banque')
        if not paiement:
            raise forms.ValidationError(
                _("A payment method must be specified")
            )
        elif paiement.type_paiement == 'check' and not (cheque and banque):
            raise forms.ValidationError(
                _("A cheque number and a bank must be specified")
            )
        return cleaned_data


class CreditSoldeForm(NewFactureForm):
    """Permet de faire des opérations sur le solde si il est activé"""
    # TODO : translate docstring to English
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


class SelectUserArticleForm(FormRevMixin, Form):
    """Selection d'un article lors de la creation d'une facture"""
    # TODO : translate docstring to English
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(Q(type_user='All') | Q(type_user='Adherent')),
        label=_("Article"),
        required=True
    )
    quantity = forms.IntegerField(
        label=_("Quantity"),
        validators=[MinValueValidator(1)],
        required=True
    )


class SelectClubArticleForm(Form):
    """Selection d'un article lors de la creation d'une facture"""
    # TODO : translate docstring to English
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(Q(type_user='All') | Q(type_user='Club')),
        label=_("Article"),
        required=True
    )
    quantity = forms.IntegerField(
        label=_("Quantity"),
        validators=[MinValueValidator(1)],
        required=True
    )

# TODO : change Facture to Invoice
class NewFactureFormPdf(Form):
    """Creation d'un pdf facture par le trésorier"""
    # TODO : translate docstring to English
    article = forms.ModelMultipleChoiceField(
        queryset=Article.objects.all(),
        label=_("Article")
    )
    number = forms.IntegerField(
        label=_("Quantity"),
        validators=[MinValueValidator(1)]
    )
    paid = forms.BooleanField(label=_("Paid"), required=False)
    # TODO : change dest field to recipient
    dest = forms.CharField(required=True, max_length=255, label=_("Recipient"))
    # TODO : change chambre field to address
    chambre = forms.CharField(required=False, max_length=10, label=_("Address"))
    # TODO : change fid field to invoice_id
    fid = forms.CharField(
        required=True,
        max_length=10,
        label=_("Invoice number")
    )

# TODO : change Facture to Invoice
class EditFactureForm(FieldPermissionFormMixin, NewFactureForm):
    """Edition d'une facture : moyen de paiement, banque, user parent"""
    # TODO : translate docstring to English
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
    """Creation d'un article. Champs : nom, cotisation, durée"""
    # TODO : translate docstring to English
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ArticleForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Article name")


class DelArticleForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs articles en vente. Choix
    parmis les modèles"""
    # TODO : translate docstring to English
    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.none(),
        label=_("Existing articles"),
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
    """Creation d'un moyen de paiement, champ text moyen et type
    permettant d'indiquer si il s'agit d'un chèque ou non pour le form"""
    # TODO : translate docstring to English
    class Meta:
        model = Paiement
        # TODO : change moyen to method and type_paiement to payment_type
        fields = ['moyen', 'type_paiement']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PaiementForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['moyen'].label = _("Payment method name")
        self.fields['type_paiement'].label = _("Payment type")
        self.fields['type_paiement'].help_text = \
            _("The payement type is use for specific behaviour.\
            The \"cheque\" type means a cheque number and a bank name\
            may be added when using this payment method.")


# TODO : change paiement to payment
class DelPaiementForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs moyens de paiements, selection
    parmis les models"""
    # TODO : translate docstring to English
    # TODO : change paiement to payment
    paiements = forms.ModelMultipleChoiceField(
        queryset=Paiement.objects.none(),
        label=_("Existing payment method"),
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
    """Creation d'une banque, field name"""
    # TODO : translate docstring to Englishh
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
    """Selection d'une ou plusieurs banques, pour suppression"""
    # TODO : translate docstrign to English
    # TODO : change banque to bank
    banques = forms.ModelMultipleChoiceField(
        queryset=Banque.objects.none(),
        label=_("Existing banks"),
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
    """Creation d'une facture, moyen de paiement, banque et numero
    de cheque"""
    # TODO : translate docstring to English
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
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
    value = forms.FloatField(
        label=_("Amount"),
        min_value=0.01,
        validators = []
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(RechargeForm, self).__init__(*args, **kwargs)

    def clean_value(self):
        value = self.cleaned_data['value']
        if value < OptionalUser.get_cached_value('min_online_payment'):
            raise forms.ValidationError(
                _("Requested amount is too small. Minimum amount possible : \
                %(min_online_amount)s €") % {
                    min_online_amount: OptionalUser.get_cached_value(
                        'min_online_payment'
                    )
                }
            )
        if value + self.user.solde > OptionalUser.get_cached_value('max_solde'):
            raise forms.ValidationError(
                _("Requested amount is too high. Your balance can't exceed \
                %(max_online_balance)s €") % {
                    max_online_balance: OptionalUser.get_cached_value(
                        'max_solde'
                    )
                }
            )
        return value
