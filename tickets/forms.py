from django import forms
from django.forms import ModelForm, Form

from .models import(
    Ticket
)

class EditTicketForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Formulaire d'edition d'un Ticket"""

    class Meta:
        model = Ticket
        exclude = ['user','assigned_staff','date']
    
    def __init__(self,*args, **kwargs):
        prefix = kwargs.pop('prefix',self.Meta.model.__name__)
        super(EditMachineForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['title'].label = _("Titre du ticket")
        self.fields['decription'].label = _("Description du ticket")
        self.field['solved'].label = _("Problème réglé ?")



class NewTicketForm(EditTicketForm):
    """ Creation d'une machine"""
    class Meta(EditeTicketForm):
            fields = '__all__'
