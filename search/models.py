from django.db import models
from django import forms
from django.forms import Form
from django.forms import ModelForm

from users.models import User
# Create your models here.

CHOICES = (
    ('0', 'Actifs'),
    ('1', 'Désactivés'),
    ('2', 'Archivés'),
)

class SearchForm(Form):
    search_field = forms.CharField(label = 'Search', max_length = 100, required=False)
    filtre = forms.MultipleChoiceField(label="Filtre utilisateur", required=False, widget =forms.CheckboxSelectMultiple,choices=CHOICES)
    date_deb = forms.DateField(required=False, label="Date de début", help_text='DD/MM/YYYY', input_formats=['%d/%m/%Y'])
    date_fin = forms.DateField(required=False, help_text='DD/MM/YYYY', input_formats=['%d/%m/%Y'], label="Date de fin")
