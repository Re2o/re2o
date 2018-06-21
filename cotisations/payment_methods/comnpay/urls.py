from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^accept/(?P<factureid>[0-9]+)$',
        views.accept_payment,
        name='accept_payment'
    ),
    url(
        r'^refuse/$',
        views.refuse_payment,
        name='refuse_payment'
    ),
    url(
        r'^ipn/$',
        views.ipn,
        name='ipn'
    ),
]
