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
notamment sur le controle trésorier)

SelectArticleForm est utilisée lors de la creation d'une facture en
parrallèle de NewFacture pour le choix des articles désirés.
(la vue correspondante est unique)

ArticleForm, BanqueForm, PaiementForm permettent aux admin d'ajouter,
éditer ou supprimer une banque/moyen de paiement ou un article
"""
from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.forms import ModelForm, Form
from django.core.validators import MinValueValidator
from .models import Article, Paiement, Facture, Banque

from re2o.field_permissions import FieldPermissionFormMixin


class NewFactureForm(ModelForm):
    """Creation d'une facture, moyen de paiement, banque et numero
    de cheque"""
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(NewFactureForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = 'Numero de chèque'
        self.fields['banque'].empty_label = "Non renseigné"
        self.fields['paiement'].empty_label = "Séléctionner\
        un moyen de paiement"
        paiement_list = Paiement.objects.filter(type_paiement=1)
        if paiement_list:
            self.fields['paiement'].widget\
                .attrs['data-cheque'] = paiement_list.first().id

    class Meta:
        model = Facture
        fields = ['paiement', 'banque', 'cheque']

    def clean(self):
        cleaned_data = super(NewFactureForm, self).clean()
        paiement = cleaned_data.get("paiement")
        cheque = cleaned_data.get("cheque")
        banque = cleaned_data.get("banque")
        if not paiement:
            raise forms.ValidationError("Le moyen de paiement est obligatoire")
        elif paiement.type_paiement == "check" and not (cheque and banque):
            raise forms.ValidationError("Le numéro de chèque et\
                la banque sont obligatoires.")
        return cleaned_data


class CreditSoldeForm(NewFactureForm):
    """Permet de faire des opérations sur le solde si il est activé"""
    class Meta(NewFactureForm.Meta):
        model = Facture
        fields = ['paiement', 'banque', 'cheque']

    def __init__(self, *args, **kwargs):
        super(CreditSoldeForm, self).__init__(*args, **kwargs)
        self.fields['paiement'].queryset = Paiement.objects.exclude(
            moyen='solde'
        ).exclude(moyen="Solde")

    montant = forms.DecimalField(max_digits=5, decimal_places=2, required=True)


class SelectUserArticleForm(Form):
    """Selection d'un article lors de la creation d'une facture"""
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(Q(type_user='All') | Q(type_user='Adherent')),
        label="Article",
        required=True
    )
    quantity = forms.IntegerField(
        label="Quantité",
        validators=[MinValueValidator(1)],
        required=True
    )


class SelectClubArticleForm(Form):
    """Selection d'un article lors de la creation d'une facture"""
    article = forms.ModelChoiceField(
        queryset=Article.objects.filter(Q(type_user='All') | Q(type_user='Club')),
        label="Article",
        required=True
    )
    quantity = forms.IntegerField(
        label="Quantité",
        validators=[MinValueValidator(1)],
        required=True
    )


class NewFactureFormPdf(Form):
    """Creation d'un pdf facture par le trésorier"""
    article = forms.ModelMultipleChoiceField(
        queryset=Article.objects.all(),
        label="Article"
    )
    number = forms.IntegerField(
        label="Quantité",
        validators=[MinValueValidator(1)]
    )
    paid = forms.BooleanField(label="Payé", required=False)
    dest = forms.CharField(required=True, max_length=255, label="Destinataire")
    chambre = forms.CharField(required=False, max_length=10, label="Adresse")
    fid = forms.CharField(
        required=True,
        max_length=10,
        label="Numéro de la facture"
    )


class EditFactureForm(FieldPermissionFormMixin, NewFactureForm):
    """Edition d'une facture : moyen de paiement, banque, user parent"""
    class Meta(NewFactureForm.Meta):
        model = Facture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Adherent'
        self.fields['user'].empty_label = "Séléctionner\
            l'adhérent propriétaire"
        self.fields['valid'].label = 'Validité de la facture'


class ArticleForm(ModelForm):
    """Creation d'un article. Champs : nom, cotisation, durée"""
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ArticleForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = "Désignation de l'article"


class DelArticleForm(Form):
    """Suppression d'un ou plusieurs articles en vente. Choix
    parmis les modèles"""
    articles = forms.ModelMultipleChoiceField(
        queryset=Article.objects.none(),
        label="Articles actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelArticleForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['articles'].queryset = instances
        else:
            self.fields['articles'].queryset = Article.objects.all()


class PaiementForm(ModelForm):
    """Creation d'un moyen de paiement, champ text moyen et type
    permettant d'indiquer si il s'agit d'un chèque ou non pour le form"""
    class Meta:
        model = Paiement
        fields = ['moyen', 'type_paiement']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(PaiementForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['moyen'].label = 'Moyen de paiement à ajouter'
        self.fields['type_paiement'].label = 'Type de paiement à ajouter'


class DelPaiementForm(Form):
    """Suppression d'un ou plusieurs moyens de paiements, selection
    parmis les models"""
    paiements = forms.ModelMultipleChoiceField(
        queryset=Paiement.objects.none(),
        label="Moyens de paiement actuels",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelPaiementForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['paiements'].queryset = instances
        else:
            self.fields['paiements'].queryset = Paiement.objects.all()


class BanqueForm(ModelForm):
    """Creation d'une banque, field name"""
    class Meta:
        model = Banque
        fields = ['name']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(BanqueForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = 'Banque à ajouter'


class DelBanqueForm(Form):
    """Selection d'une ou plusieurs banques, pour suppression"""
    banques = forms.ModelMultipleChoiceField(
        queryset=Banque.objects.none(),
        label="Banques actuelles",
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelBanqueForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['banques'].queryset = instances
        else:
            self.fields['banques'].queryset = Banque.objects.all()
