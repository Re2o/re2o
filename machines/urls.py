# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
"""machines.urls
The defined URLs for the Machines app
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^new_machine/(?P<userid>[0-9]+)$", views.new_machine, name="new-machine"),
    url(
        r"^edit_interface/(?P<interfaceid>[0-9]+)$",
        views.edit_interface,
        name="edit-interface",
    ),
    url(r"^del_machine/(?P<machineid>[0-9]+)$", views.del_machine, name="del-machine"),
    url(
        r"^new_interface/(?P<machineid>[0-9]+)$",
        views.new_interface,
        name="new-interface",
    ),
    url(
        r"^del_interface/(?P<interfaceid>[0-9]+)$",
        views.del_interface,
        name="del-interface",
    ),
    url(r"^add_machinetype/$", views.add_machinetype, name="add-machinetype"),
    url(
        r"^edit_machinetype/(?P<machinetypeid>[0-9]+)$",
        views.edit_machinetype,
        name="edit-machinetype",
    ),
    url(r"^del_machinetype/$", views.del_machinetype, name="del-machinetype"),
    url(r"^index_machinetype/$", views.index_machinetype, name="index-machinetype"),
    url(r"^add_iptype/$", views.add_iptype, name="add-iptype"),
    url(r"^edit_iptype/(?P<iptypeid>[0-9]+)$", views.edit_iptype, name="edit-iptype"),
    url(r"^del_iptype/$", views.del_iptype, name="del-iptype"),
    url(r"^index_iptype/$", views.index_iptype, name="index-iptype"),
    url(r"^add_extension/$", views.add_extension, name="add-extension"),
    url(
        r"^edit_extension/(?P<extensionid>[0-9]+)$",
        views.edit_extension,
        name="edit-extension",
    ),
    url(r"^del_extension/$", views.del_extension, name="del-extension"),
    url(r"^add_soa/$", views.add_soa, name="add-soa"),
    url(r"^edit_soa/(?P<soaid>[0-9]+)$", views.edit_soa, name="edit-soa"),
    url(r"^del_soa/$", views.del_soa, name="del-soa"),
    url(r"^add_mx/$", views.add_mx, name="add-mx"),
    url(r"^edit_mx/(?P<mxid>[0-9]+)$", views.edit_mx, name="edit-mx"),
    url(r"^del_mx/$", views.del_mx, name="del-mx"),
    url(r"^add_txt/$", views.add_txt, name="add-txt"),
    url(r"^edit_txt/(?P<txtid>[0-9]+)$", views.edit_txt, name="edit-txt"),
    url(r"^del_txt/$", views.del_txt, name="del-txt"),
    url(r"^add_dname/$", views.add_dname, name="add-dname"),
    url(r"^edit_dname/(?P<dnameid>[0-9]+)$", views.edit_dname, name="edit-dname"),
    url(r"^del_dname/$", views.del_dname, name="del-dname"),
    url(r"^add_ns/$", views.add_ns, name="add-ns"),
    url(r"^edit_ns/(?P<nsid>[0-9]+)$", views.edit_ns, name="edit-ns"),
    url(r"^del_ns/$", views.del_ns, name="del-ns"),
    url(r"^add_srv/$", views.add_srv, name="add-srv"),
    url(r"^edit_srv/(?P<srvid>[0-9]+)$", views.edit_srv, name="edit-srv"),
    url(r"^del_srv/$", views.del_srv, name="del-srv"),
    url(r"^new_sshfp/(?P<machineid>[0-9]+)$", views.new_sshfp, name="new-sshfp"),
    url(r"^edit_sshfp/(?P<sshfpid>[0-9]+)$", views.edit_sshfp, name="edit-sshfp"),
    url(r"^del_sshfp/(?P<sshfpid>[0-9]+)$", views.del_sshfp, name="del-sshfp"),
    url(r"^index_sshfp/(?P<machineid>[0-9]+)$", views.index_sshfp, name="index-sshfp"),
    url(r"^index_extension/$", views.index_extension, name="index-extension"),
    url(r"^add_alias/(?P<interfaceid>[0-9]+)$", views.add_alias, name="add-alias"),
    url(r"^edit_alias/(?P<domainid>[0-9]+)$", views.edit_alias, name="edit-alias"),
    url(r"^del_alias/(?P<interfaceid>[0-9]+)$", views.del_alias, name="del-alias"),
    url(
        r"^index_alias/(?P<interfaceid>[0-9]+)$", views.index_alias, name="index-alias"
    ),
    url(
        r"^new_ipv6list/(?P<interfaceid>[0-9]+)$",
        views.new_ipv6list,
        name="new-ipv6list",
    ),
    url(
        r"^edit_ipv6list/(?P<ipv6listid>[0-9]+)$",
        views.edit_ipv6list,
        name="edit-ipv6list",
    ),
    url(
        r"^del_ipv6list/(?P<ipv6listid>[0-9]+)$",
        views.del_ipv6list,
        name="del-ipv6list",
    ),
    url(r"^index_ipv6/(?P<interfaceid>[0-9]+)$", views.index_ipv6, name="index-ipv6"),
    url(r"^add_service/$", views.add_service, name="add-service"),
    url(
        r"^edit_service/(?P<serviceid>[0-9]+)$", views.edit_service, name="edit-service"
    ),
    url(r"^del_service/$", views.del_service, name="del-service"),
    url(
        r"^regen_service/(?P<serviceid>[0-9]+)$",
        views.regen_service,
        name="regen-service",
    ),
    url(r"^index_service/$", views.index_service, name="index-service"),
    url(r"^add_role/$", views.add_role, name="add-role"),
    url(r"^edit_role/(?P<roleid>[0-9]+)$", views.edit_role, name="edit-role"),
    url(r"^del_role/$", views.del_role, name="del-role"),
    url(r"^index_role/$", views.index_role, name="index-role"),
    url(r"^add_vlan/$", views.add_vlan, name="add-vlan"),
    url(r"^edit_vlan/(?P<vlanid>[0-9]+)$", views.edit_vlan, name="edit-vlan"),
    url(r"^del_vlan/$", views.del_vlan, name="del-vlan"),
    url(r"^index_vlan/$", views.index_vlan, name="index-vlan"),
    url(r"^add_nas/$", views.add_nas, name="add-nas"),
    url(r"^edit_nas/(?P<nasid>[0-9]+)$", views.edit_nas, name="edit-nas"),
    url(r"^del_nas/$", views.del_nas, name="del-nas"),
    url(r"^index_nas/$", views.index_nas, name="index-nas"),
    url(r"^$", views.index, name="index"),
    url(r"index_portlist/$", views.index_portlist, name="index-portlist"),
    url(
        r"^edit_portlist/(?P<ouvertureportlistid>[0-9]+)$",
        views.edit_portlist,
        name="edit-portlist",
    ),
    url(
        r"^del_portlist/(?P<ouvertureportlistid>[0-9]+)$",
        views.del_portlist,
        name="del-portlist",
    ),
    url(r"^add_portlist/$", views.add_portlist, name="add-portlist"),
    url(
        r"^port_config/(?P<interfaceid>[0-9]+)$",
        views.configure_ports,
        name="port-config",
    ),
]
