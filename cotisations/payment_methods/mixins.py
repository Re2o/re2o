from django.db import models

from cotisations.models import Paiement


class PaymentMethodMixin:
    """The base class for payment models. They should inherit from this."""
    payment = models.OneToOneField(
        Paiement,
        related_name='payment_method',
        editable=False
    )

    def end_payment(self, invoice, request):
        """Redefine this method in order to get a different ending to the
        payment session if you whish.

        Must return a HttpResponse-like object.
        """
        return self.payment.end_payment(
            invoice, request, use_payment_method=False)
