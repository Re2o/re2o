from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.aff_tickets, name='aff-tickets'),
    url(r'^ticket/(?P<ticketid>[0-9]+)$', views.aff_ticket, name='aff-ticket'),
    url(r'^new_ticket/$',views.new_ticket,name='new-ticket'),
]
