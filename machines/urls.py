from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_machine/(?P<userid>[0-9]+)$', views.new_machine, name='new-machine'),
    url(r'^edit_machine/(?P<interfaceid>[0-9]+)$', views.edit_machine, name='edit-machine'),
    url(r'^new_interface/(?P<machineid>[0-9]+)$', views.new_interface, name='new-interface'),
    url(r'^add_machinetype/$', views.add_machinetype, name='add-machinetype'),
    url(r'^edit_machinetype/(?P<machinetypeid>[0-9]+)$', views.edit_machinetype, name='edit-machinetype'),
    url(r'^del_machinetype/$', views.del_machinetype, name='del-machinetype'),
    url(r'^index_machinetype/$', views.index_machinetype, name='index-machinetype'),
    url(r'^$', views.index, name='index'),
]
