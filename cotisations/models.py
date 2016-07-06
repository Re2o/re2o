from django.db import models
from django import forms
from django.forms import ModelForm


class Facture(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    banque = models.ForeignKey('Banque', on_delete=models.PROTECT, blank=True, null=True)
    cheque = models.CharField(max_length=255, blank=True)
    number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name) + ' ' + str(self.date) + ' ' + str(self.user)

class Article(models.Model):
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    cotisation = models.BooleanField()
    duration = models.IntegerField(help_text="Durée exprimée en mois entiers", blank=True, null=True)

    def __str__(self):
        return self.name

class Banque(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Paiement(models.Model):
    moyen = models.CharField(max_length=255)

    def __str__(self):
        return self.moyen

class Cotisation(models.Model):
    facture = models.OneToOneField('Facture', on_delete=models.PROTECT)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return str(self.facture)

class NewFactureForm(ModelForm):
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.all(), label="Article")

    def __init__(self, *args, **kwargs):
        super(NewFactureForm, self).__init__(*args, **kwargs)
        self.fields['number'].label = 'Quantité'
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = 'Numero de chèque'
        self.fields['banque'].empty_label = "Non renseigné"
        self.fields['paiement'].empty_label = "Séléctionner un moyen de paiement"

    class Meta:
        model = Facture
        fields = ['paiement','banque','cheque','number']

    def clean(self):
        cleaned_data=super(NewFactureForm, self).clean()
        paiement = cleaned_data.get("paiement")
        cheque = cleaned_data.get("cheque")
        banque = cleaned_data.get("banque")
        if paiement.moyen=="chèque" and not (cheque and banque):
            raise forms.ValidationError("Le numero de chèque et la banque sont obligatoires")
        return cleaned_data

class EditFactureForm(NewFactureForm):
    class Meta(NewFactureForm.Meta):
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Adherent'
        self.fields['name'].label = 'Designation'
        self.fields['prix'].label = 'Prix unitaire'
        self.fields['user'].empty_label = "Séléctionner l'adhérent propriétaire"
        self.fields.pop('article')
