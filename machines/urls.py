# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
    url(r'^add_mx/$', views.add_mx, name='add-mx'),
    url(r'^edit_mx/(?P<mxid>[0-9]+)$', views.edit_mx, name='edit-mx'),
    url(r'^del_mx/$', views.del_mx, name='del-mx'),
    url(r'^add_ns/$', views.add_ns, name='add-ns'),
    url(r'^edit_ns/(?P<nsid>[0-9]+)$', views.edit_ns, name='edit-ns'),
    url(r'^del_ns/$', views.del_ns, name='del-ns'),
    url(r'^index_extension/$', views.index_extension, name='index-extension'),
    url(r'^add_alias/(?P<interfaceid>[0-9]+)$', views.add_alias, name='add-alias'),
    url(r'^edit_alias/(?P<aliasid>[0-9]+)$', views.edit_alias, name='edit-alias'),
    url(r'^del_alias/(?P<interfaceid>[0-9]+)$', views.del_alias, name='del-alias'),
    url(r'^index_alias/(?P<interfaceid>[0-9]+)$', views.index_alias, name='index-alias'),
    url(r'^add_service/$', views.add_service, name='add-service'),
    url(r'^edit_service/(?P<serviceid>[0-9]+)$', views.edit_service, name='edit-service'),
    url(r'^del_service/$', views.del_service, name='del-service'),
    url(r'^index_service/$', views.index_service, name='index-service'),
    url(r'^history/(?P<object>machine)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>interface)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>machinetype)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>extension)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>mx)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>ns)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>iptype)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>alias)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^history/(?P<object>service)/(?P<id>[0-9]+)$', views.history, name='history'),
    url(r'^$', views.index, name='index'),
    url(r'^rest/mac-ip/$', views.mac_ip, name='mac-ip'),
    url(r'^rest/login/$', views.login_user, name='login'),
    url(r'^rest/mac-ip-dns/$', views.mac_ip_dns, name='mac-ip-dns'),
    url(r'^rest/alias/$', views.alias, name='alias'),
    url(r'^rest/corresp/$', views.corresp, name='corresp'),
    url(r'^rest/mx/$', views.mx, name='mx'),
    url(r'^rest/ns/$', views.ns, name='ns'),
    url(r'^rest/zones/$', views.zones, name='zones'),
    ]
