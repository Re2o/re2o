from django.db import models
from django.shortcuts import render

from cotisations.models import Paiement as BasePayment

from .aes_field import AESEncryptedField
from .views import comnpay


class ComnpayPayment(models.Model):
    """
    The model allowing you to pay with COMNPAY. It redefines post_payment
    method. See `cotisations.models.Paiement for further details.
    """
    payment = models.OneToOneField(BasePayment, related_name='payment_method')

    payment_credential = models.CharField(
        max_length=255,
        default='',
        blank=True
    )
    payment_pass = AESEncryptedField(
        max_length=255,
        null=True,
        blank=True,
    )

    def end_payment(self, invoice, request):
        invoice.valid = False
        invoice.save()
        content = comnpay(invoice, request)
        return render(request, 'cotisations/payment.html', content)
