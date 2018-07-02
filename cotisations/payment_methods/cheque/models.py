from django.db import models
from django.shortcuts import redirect
from django.urls import reverse

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class ChequePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """
    payment = models.OneToOneField(
        Paiement,
        related_name='payment_method',
        editable=False
    )
    def end_payment(self, invoice, request):
        invoice.valid = False
        invoice.save()
        return redirect(reverse(
            'cotisations:cheque:validate',
            kwargs={'invoice_pk': invoice.pk}
        ))
