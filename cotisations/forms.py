from django import forms
from django.forms import ModelForm, Form
from django import forms
from .models import Article, Paiement, Facture, Banque, Vente

class NewFactureForm(ModelForm):
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), label="Article", widget=forms.CheckboxSelectMultiple())

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
        if paiement.moyen=="chèque" and not (cheque and banque):
            raise forms.ValidationError("Le numero de chèque et la banque sont obligatoires")
        return cleaned_data

class SelectArticleForm(Form):
    article = forms.ModelChoiceField(queryset=Article.objects.all(), label="Article")
    quantity = forms.IntegerField(label="Quantité")

class NewFactureFormPdf(Form):
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), label="Article")
    number = forms.IntegerField(label="Quantité")
    paid = forms.BooleanField(label="Payé", required=False)
    dest = forms.CharField(required=True, max_length=255, label="Destinataire")
    chambre = forms.CharField(required=False, max_length=10, label="Adresse")
    fid = forms.CharField(required=True, max_length=10, label="Numéro de la facture")

class EditFactureForm(NewFactureForm):
    class Meta(NewFactureForm.Meta):
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Adherent'
        self.fields['user'].empty_label = "Séléctionner l'adhérent propriétaire"
        self.fields.pop('article')

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
