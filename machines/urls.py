from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_machine/(?P<userid>[0-9]+)$', views.new_machine, name='new-machine'),
    url(r'^edit_machine/(?P<interfaceid>[0-9]+)$', views.edit_machine, name='edit-machine'),
    url(r'^new_interface/(?P<machineid>[0-9]+)$', views.new_interface, name='new-interface'),
    url(r'^$', views.index, name='index'),
]
