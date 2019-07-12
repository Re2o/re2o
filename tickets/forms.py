from django import forms
from django.forms import ModelForm, Form
from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from django.utils.translation import ugettext_lazy as _

from .models import(
    Ticket
)

class EditTicketForm(FormRevMixin, ModelForm):
    """Formulaire d'edition d'un Ticket"""
    
    #def __init__(self,*args, **kwargs):
        #prefix = kwargs.pop('prefix',self.Meta.model.__name__)
        #super(EditTicketForm, self).__init__(*args, prefix=prefix, **kwargs)
        #self.fields['title'].label = _("Titre du ticket")
        #self.fields['decription'].label = _("Description du ticket")
        #self.fields['solved'].label = _("Problème réglé ?")

    class Meta:
        model = Ticket
        exclude = ['user','assigned_staff','date']


class NewTicketForm(ModelForm):
    """ Creation d'une machine"""
    
    email = forms.EmailField(required=False)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'email']

    #def __init(self,*args, **kwargs):
        #prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        #super(NewTicketForm, self).__init__(*args, prefix=prefix, **kwargs)
