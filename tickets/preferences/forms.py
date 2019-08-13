from django import forms
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _

from .models import Preferences

class EditPreferencesForm(ModelForm):
    """ Edition des préférences des tickets """
    class Meta:
        model = Preferences
        fields = '__all__'
