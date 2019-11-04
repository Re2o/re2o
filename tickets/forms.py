from django import forms
from django.forms import ModelForm, Form
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from django.utils.translation import ugettext_lazy as _

from .models import Ticket


class NewTicketForm(ModelForm):
    """ Creation of a ticket"""

    email = forms.EmailField(required=False)

    class Meta:
        model = Ticket
        fields = ["title", "description", "email"]


class ChangeStatusTicketForm(ModelForm):
    """ Change ticket status"""

    class Meta:
        model = Ticket
        fields = []
