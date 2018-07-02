from django import forms
from django.utils.translation import ugettext_lazy as _l

from re2o.mixins import FormRevMixin
from cotisations.models import Facture as Invoice


class InvoiceForm(FormRevMixin, forms.ModelForm):
    """A simple form to get the bank a the cheque number."""
    class Meta:
        model = Invoice
        fields = ['banque', 'cheque']
