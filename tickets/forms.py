from django import forms
from django.forms import ModelForm, Form
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from django.utils.translation import ugettext_lazy as _

from .models import(
    Ticket,
)

class EditTicketForm(FormRevMixin, ModelForm):
    """Formulaire d'edition d'un Ticket"""
    class Meta:
        model = Ticket
        exclude = ['user','assigned_staff','date']


class NewTicketForm(ModelForm):
    """ Creation d'une machine"""
    email = forms.EmailField(required=False)
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'email']
"""
class EditPreferencesForm(ModelForm):
    class Meta:
        model = Preferences
        fields = '__all__'
"""

class ChangeStatusTicketForm(ModelForm):
    """ Passe un Ticket en résolu """
    class Meta:
        model = Ticket
        fields = []

