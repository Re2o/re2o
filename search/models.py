from django.db import models
from django import forms
from django.forms import Form
from django.forms import ModelForm

from users.models import User
# Create your models here.

class SearchForm(Form):
    search_field = forms.CharField(label = 'Search', max_length = 100)
