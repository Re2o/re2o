class PaymentMethodMixin:
    """The base class for payment models. They should inherit from this."""

    def end_payment(self, invoice, request):
        """Redefine this method in order to get a different ending to the
        payment session if you whish.

        Must return a HttpResponse-like object.
        """
        return self.payment.end_payment(
            invoice, request, use_payment_method=False)
