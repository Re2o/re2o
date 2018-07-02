def find_payment_method(payment):
    from cotisations.payment_methods import PAYMENT_METHODS
    for method in PAYMENT_METHODS:
        try:
            o = method.PaymentMethod.objects.get(payment=payment)
            return o
        except method.PaymentMethod.DoesNotExist:
            pass
    return None
