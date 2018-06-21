from django.conf.urls import include, url

from . import comnpay, cheque


urlpatterns = [
    url(r'^comnpay/', include(comnpay.urls, namespace='comnpay')),
    url(r'^cheque/', include(cheque.urls, namespace='cheque')),
]
