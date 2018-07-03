from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin

from .aes_field import AESEncryptedField
from .comnpay import Transaction


class ComnpayPayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with COMNPAY.
    """
    payment = models.OneToOneField(
        Paiement,
        related_name='payment_method',
        editable=False
    )
    payment_credential = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name=_l("ComNpay VAD Number"),
    )
    payment_pass = AESEncryptedField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_l("ComNpay Secret Key"),
    )

    def end_payment(self, invoice, request):
        """
        Build a request to start the negociation with Comnpay by using
        a facture id, the price and the secret transaction data stored in
        the preferences.
        """
        invoice.valid = False
        invoice.save()
        host = request.get_host()
        p = Transaction(
            str(self.payment_credential),
            str(self.payment_pass),
            'https://' + host + reverse(
                'cotisations:comnpay:accept_payment',
                kwargs={'factureid': invoice.id}
            ),
            'https://' + host + reverse('cotisations:comnpay:refuse_payment'),
            'https://' + host + reverse('cotisations:comnpay:ipn'),
            "",
            "D"
        )
        r = {
            'action': 'https://secure.homologation.comnpay.com',
            'method': 'POST',
            'content': p.buildSecretHTML(
                _("Pay invoice no : ")+str(invoice.id),
                invoice.prix_total(),
                idTransaction=str(invoice.id)
            ),
            'amount': invoice.prix_total(),
        }
        return render(request, 'cotisations/payment.html', r)
