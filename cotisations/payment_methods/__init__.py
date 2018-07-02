from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _l

from . import comnpay, cheque


urlpatterns = [
    url(r'^comnpay/', include(comnpay.urls, namespace='comnpay')),
    url(r'^cheque/', include(cheque.urls, namespace='cheque')),
]

PAYMENT_METHODS = [
    comnpay,
    cheque,
]


def find_payment_method(payment):
    for method in PAYMENT_METHODS:
        try:
            o = method.PaymentMethod.objects.get(payment=payment)
            return o
        except method.PaymentMethod.DoesNotExist:
            pass
    return None
