from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.aff_tickets, name='index des tickets'),
    url(r'^new_ticket/(?P<userid>[0-9]+)$',
        views.new_ticket,
        name='new-ticket'),
]
