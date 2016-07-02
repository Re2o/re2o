from django.db import models
from django import forms
from django.forms import ModelForm

from users.models import User

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
    duration = models.DurationField(blank=True, null=True)

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
    facture = models.ForeignKey('Facture', on_delete=models.PROTECT)
    date_start = models.DateTimeField(auto_now_add=True)
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

    class Meta:
        model = Facture
        exclude = ['user', 'prix', 'name']

class EditFactureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditFactureForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Adherent'
        self.fields['number'].label = 'Quantité'
        self.fields['cheque'].required = False
        self.fields['banque'].required = False
        self.fields['cheque'].label = 'Numero de chèque'
        self.fields['name'].label = 'Designation'
        self.fields['prix'].label = 'Prix unitaire'

    class Meta:
        model = Facture
        fields = '__all__'
