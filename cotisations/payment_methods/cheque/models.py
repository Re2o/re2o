from django.db import models
from django.shortcuts import redirect
from django.urls import reverse

from cotisations.models import Paiement as BasePayment


class ChequePayment(models.Model):
    """
    The model allowing you to pay with a cheque. It redefines post_payment
    method. See `cotisations.models.Paiement for further details.
    """
    payment = models.OneToOneField(BasePayment, related_name='payment_method')

    def end_payment(self, invoice, request):
        invoice.valid = False
        invoice.save()
        return redirect(reverse(
            'cotisations:cheque:validate',
            kwargs={'invoice_pk': invoice.pk}
        ))
