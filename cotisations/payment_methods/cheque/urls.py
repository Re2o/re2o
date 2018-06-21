from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^validate/(?P<invoice_pk>[0-9]+)$',
        views.cheque,
        name='validate'
    )
]
