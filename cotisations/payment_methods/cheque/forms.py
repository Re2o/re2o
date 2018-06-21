from django import forms
from django.utils.translation import ugettext_lazy as _l

from cotisations.models import Banque as Bank


class ChequeForm(forms.Form):
    """A simple form to get the bank a the cheque number."""
    bank = forms.ModelChoiceField(Bank.objects.all(), label=_l("Bank"))
    number = forms.CharField(label=_l("Cheque number"))
