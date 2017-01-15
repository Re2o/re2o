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

from django import forms
from django.forms import ModelForm, Form
from django import forms
from django.core.validators import MinValueValidator
from .models import Article, Paiement, Facture, Banque, Vente

class NewFactureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewFactureForm, self).__init__(*args, **kwargs)
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = 'Numero de chèque'
        self.fields['banque'].empty_label = "Non renseigné"
        self.fields['paiement'].empty_label = "Séléctionner un moyen de paiement"

    class Meta:
        model = Facture
        fields = ['paiement','banque','cheque']

    def clean(self):
        cleaned_data=super(NewFactureForm, self).clean()
        paiement = cleaned_data.get("paiement")
        cheque = cleaned_data.get("cheque")
        banque = cleaned_data.get("banque")
        if not paiement:
            raise forms.ValidationError("Le moyen de paiement est obligatoire")
        elif paiement.moyen=="chèque" and not (cheque and banque):
            raise forms.ValidationError("Le numero de chèque et la banque sont obligatoires")
        return cleaned_data

class SelectArticleForm(Form):
    article = forms.ModelChoiceField(queryset=Article.objects.all(), label="Article", required=True)
    quantity = forms.IntegerField(label="Quantité", validators=[MinValueValidator(1)], required=True)

class NewFactureFormPdf(Form):
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), label="Article")
    number = forms.IntegerField(label="Quantité", validators=[MinValueValidator(1)])
    paid = forms.BooleanField(label="Payé", required=False)
    dest = forms.CharField(required=True, max_length=255, label="Destinataire")
    chambre = forms.CharField(required=False, max_length=10, label="Adresse")
    fid = forms.CharField(required=True, max_length=10, label="Numéro de la facture")

class EditFactureForm(NewFactureForm):
    class Meta(NewFactureForm.Meta):
        fields = ['paiement','banque','cheque','user']

    def __init__(self, *args, **kwargs):
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Adherent'
        self.fields['user'].empty_label = "Séléctionner l'adhérent propriétaire"

class TrezEditFactureForm(EditFactureForm):
    class Meta(EditFactureForm.Meta):
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TrezEditFactureForm, self).__init__(*args, **kwargs)
        self.fields['valid'].label = 'Validité de la facture'
        self.fields['control'].label = 'Controle de la facture'


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Désignation de l'article"

class DelArticleForm(ModelForm):
    articles = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), label="Articles actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        fields = ['articles']
        model = Article

class PaiementForm(ModelForm):
    class Meta:
        model = Paiement
        fields = ['moyen']

    def __init__(self, *args, **kwargs):
        super(PaiementForm, self).__init__(*args, **kwargs)
        self.fields['moyen'].label = 'Moyen de paiement à ajouter'

class DelPaiementForm(ModelForm):
    paiements = forms.ModelMultipleChoiceField(queryset=Paiement.objects.all(), label="Moyens de paiement actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['moyen']
        model = Paiement

class BanqueForm(ModelForm):
    class Meta:
        model = Banque
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(BanqueForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Banque à ajouter'

class DelBanqueForm(ModelForm):
    banques = forms.ModelMultipleChoiceField(queryset=Banque.objects.all(), label="Banques actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['name']
        model = Banque
