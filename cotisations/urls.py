from django.conf.urls import url

from . import views

app_name = 'cotisations'
urlpatterns = [
    url(r'^new_facture/(?P<userid>[0-9]+)$', views.new_facture, name='new-facture'),
    url(r'^edit_facture/(?P<factureid>[0-9]+)$', views.edit_facture, name='edit-facture'),
    url(r'^del_facture/(?P<factureid>[0-9]+)$', views.del_facture, name='del-facture'),
    url(r'^facture_pdf/(?P<factureid>[0-9]+)$', views.facture_pdf, name='facture-pdf'),
    url(r'^new_facture_pdf/$', views.new_facture_pdf, name='new-facture-pdf'),
    url(r'^add_article/$', views.add_article, name='add-article'),
    url(r'^edit_article/(?P<articleid>[0-9]+)$', views.edit_article, name='edit-article'),
    url(r'^del_article/$', views.del_article, name='del-article'),
    url(r'^add_paiement/$', views.add_paiement, name='add-paiement'),
    url(r'^edit_paiement/(?P<paiementid>[0-9]+)$', views.edit_paiement, name='edit-paiement'),
    url(r'^del_paiement/$', views.del_paiement, name='del-paiement'),
    url(r'^add_banque/$', views.add_banque, name='add-banque'),
    url(r'^edit_banque/(?P<banqueid>[0-9]+)$', views.edit_banque, name='edit-banque'),
    url(r'^del_banque/$', views.del_banque, name='del-banque'),
    url(r'^index_article/$', views.index_article, name='index-article'),
    url(r'^index_banque/$', views.index_banque, name='index-banque'),
    url(r'^index_paiement/$', views.index_paiement, name='index-paiement'),
    url(r'^history/(?P<object>facture)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>article)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>paiement)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>banque)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^control/$', views.control, name='control'),
    url(r'^$', views.index, name='index'),
]


