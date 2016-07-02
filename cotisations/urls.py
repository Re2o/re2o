from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_facture/(?P<userid>[0-9]+)$', views.new_facture, name='new-facture'),
    url(r'^edit_facture/(?P<factureid>[0-9]+)$', views.edit_facture, name='edit-facture'),
    url(r'^$', views.index, name='index'),
]


