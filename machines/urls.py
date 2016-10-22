from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_machine/(?P<userid>[0-9]+)$', views.new_machine, name='new-machine'),
    url(r'^edit_interface/(?P<interfaceid>[0-9]+)$', views.edit_interface, name='edit-interface'),
    url(r'^del_machine/(?P<machineid>[0-9]+)$', views.del_machine, name='del-machine'),
    url(r'^new_interface/(?P<machineid>[0-9]+)$', views.new_interface, name='new-interface'),
    url(r'^del_interface/(?P<interfaceid>[0-9]+)$', views.del_interface, name='del-interface'),
    url(r'^add_machinetype/$', views.add_machinetype, name='add-machinetype'),
    url(r'^edit_machinetype/(?P<machinetypeid>[0-9]+)$', views.edit_machinetype, name='edit-machinetype'),
    url(r'^del_machinetype/$', views.del_machinetype, name='del-machinetype'),
    url(r'^index_machinetype/$', views.index_machinetype, name='index-machinetype'),
    url(r'^add_iptype/$', views.add_iptype, name='add-iptype'),
    url(r'^edit_iptype/(?P<iptypeid>[0-9]+)$', views.edit_iptype, name='edit-iptype'),
    url(r'^del_iptype/$', views.del_iptype, name='del-iptype'),
    url(r'^index_iptype/$', views.index_iptype, name='index-iptype'),
    url(r'^add_extension/$', views.add_extension, name='add-extension'),
    url(r'^edit_extension/(?P<extensionid>[0-9]+)$', views.edit_extension, name='edit-extension'),
    url(r'^del_extension/$', views.del_extension, name='del-extension'),
    url(r'^index_extension/$', views.index_extension, name='index-extension'),
    url(r'^history/(?P<object>machine)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>interface)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>machinetype)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>extension)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>iptype)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^$', views.index, name='index'),
    url(r'^rest/mac-ip/$', views.mac_ip, name='mac-ip'),
    url(r'^rest/mac-ip-dns/$', views.mac_ip_dns, name='mac-ip-dns'),
]
