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

from django.urls import path

from . import views
from . import views_autocomplete

app_name = "machines"

urlpatterns = [
    path("new_machine/<int:userid>", views.new_machine, name="new-machine"),
    path(
        "edit_interface/<int:interfaceid>",
        views.edit_interface,
        name="edit-interface",
    ),
    path("del_machine/<int:machineid>", views.del_machine, name="del-machine"),
    path(
        "new_interface/<int:machineid>",
        views.new_interface,
        name="new-interface",
    ),
    path(
        "del_interface/<int:interfaceid>",
        views.del_interface,
        name="del-interface",
    ),
    path("add_machinetype", views.add_machinetype, name="add-machinetype"),
    path(
        "edit_machinetype/<int:machinetypeid>",
        views.edit_machinetype,
        name="edit-machinetype",
    ),
    path("del_machinetype", views.del_machinetype, name="del-machinetype"),
    path("index_machinetype", views.index_machinetype, name="index-machinetype"),
    path("add_iptype", views.add_iptype, name="add-iptype"),
    path("edit_iptype/<int:iptypeid>", views.edit_iptype, name="edit-iptype"),
    path("del_iptype", views.del_iptype, name="del-iptype"),
    path("index_iptype", views.index_iptype, name="index-iptype"),
    path("add_extension", views.add_extension, name="add-extension"),
    path(
        "edit_extension/<int:extensionid>",
        views.edit_extension,
        name="edit-extension",
    ),
    path("del_extension", views.del_extension, name="del-extension"),
    path("add_soa", views.add_soa, name="add-soa"),
    path("edit_soa/<int:soaid>", views.edit_soa, name="edit-soa"),
    path("del_soa", views.del_soa, name="del-soa"),
    path("add_mx", views.add_mx, name="add-mx"),
    path("edit_mx/<int:mxid>", views.edit_mx, name="edit-mx"),
    path("del_mx", views.del_mx, name="del-mx"),
    path("add_txt", views.add_txt, name="add-txt"),
    path("edit_txt/<int:txtid>", views.edit_txt, name="edit-txt"),
    path("del_txt", views.del_txt, name="del-txt"),
    path("add_dname", views.add_dname, name="add-dname"),
    path("edit_dname/<int:dnameid>", views.edit_dname, name="edit-dname"),
    path("del_dname", views.del_dname, name="del-dname"),
    path("add_ns", views.add_ns, name="add-ns"),
    path("edit_ns/<int:nsid>", views.edit_ns, name="edit-ns"),
    path("del_ns", views.del_ns, name="del-ns"),
    path("add_srv", views.add_srv, name="add-srv"),
    path("edit_srv/<int:srvid>", views.edit_srv, name="edit-srv"),
    path("del_srv", views.del_srv, name="del-srv"),
    path("new_sshfp/<int:machineid>", views.new_sshfp, name="new-sshfp"),
    path("edit_sshfp/<int:sshfpid>", views.edit_sshfp, name="edit-sshfp"),
    path("del_sshfp/<int:sshfpid>", views.del_sshfp, name="del-sshfp"),
    path("index_sshfp/<int:machineid>", views.index_sshfp, name="index-sshfp"),
    path("index_extension", views.index_extension, name="index-extension"),
    path("add_alias/<int:interfaceid>", views.add_alias, name="add-alias"),
    path("edit_alias/<int:domainid>", views.edit_alias, name="edit-alias"),
    path("del_alias/<int:interfaceid>", views.del_alias, name="del-alias"),
    path(
        "index_alias/<int:interfaceid>", views.index_alias, name="index-alias"
    ),
    path(
        "new_ipv6list/<int:interfaceid>",
        views.new_ipv6list,
        name="new-ipv6list",
    ),
    path(
        "edit_ipv6list/<int:ipv6listid>",
        views.edit_ipv6list,
        name="edit-ipv6list",
    ),
    path(
        "del_ipv6list/<int:ipv6listid>",
        views.del_ipv6list,
        name="del-ipv6list",
    ),
    path("index_ipv6/<int:interfaceid>", views.index_ipv6, name="index-ipv6"),
    path("add_service", views.add_service, name="add-service"),
    path(
        "edit_service/<int:serviceid>", views.edit_service, name="edit-service"
    ),
    path("del_service", views.del_service, name="del-service"),
    path(
        "regen_service/<int:serviceid>",
        views.regen_service,
        name="regen-service",
    ),
    path("index_service", views.index_service, name="index-service"),
    path("add_role", views.add_role, name="add-role"),
    path("edit_role/<int:roleid>", views.edit_role, name="edit-role"),
    path("del_role", views.del_role, name="del-role"),
    path("index_role", views.index_role, name="index-role"),
    path("add_vlan", views.add_vlan, name="add-vlan"),
    path("edit_vlan/<int:vlanid>", views.edit_vlan, name="edit-vlan"),
    path("del_vlan", views.del_vlan, name="del-vlan"),
    path("index_vlan", views.index_vlan, name="index-vlan"),
    path("add_nas", views.add_nas, name="add-nas"),
    path("edit_nas/<int:nasid>", views.edit_nas, name="edit-nas"),
    path("del_nas", views.del_nas, name="del-nas"),
    path("index_nas", views.index_nas, name="index-nas"),
    path("", views.index, name="index"),
    path("index_portlist", views.index_portlist, name="index-portlist"),
    path(
        "edit_portlist/<int:ouvertureportlistid>",
        views.edit_portlist,
        name="edit-portlist",
    ),
    path(
        "del_portlist/<int:ouvertureportlistid>",
        views.del_portlist,
        name="del-portlist",
    ),
    path("add_portlist", views.add_portlist, name="add-portlist"),
    path(
        "port_config/<int:interfaceid>",
        views.configure_ports,
        name="port-config",
    ),
    ### Autocomplete Views
    path('vlan-autocomplete', views_autocomplete.VlanAutocomplete.as_view(), name='vlan-autocomplete',),
    path('interface-autocomplete', views_autocomplete.InterfaceAutocomplete.as_view(), name='interface-autocomplete',),
    path('machine-autocomplete', views_autocomplete.MachineAutocomplete.as_view(), name='machine-autocomplete',),
    path('machinetype-autocomplete', views_autocomplete.MachineTypeAutocomplete.as_view(), name='machinetype-autocomplete',),
    path('iptype-autocomplete', views_autocomplete.IpTypeAutocomplete.as_view(), name='iptype-autocomplete',),
    path('extension-autocomplete', views_autocomplete.ExtensionAutocomplete.as_view(), name='extension-autocomplete',),
    path('domain-autocomplete', views_autocomplete.DomainAutocomplete.as_view(), name='domain-autocomplete',),
    path('ouvertureportlist-autocomplete', views_autocomplete.OuverturePortListAutocomplete.as_view(), name='ouvertureportlist-autocomplete',),
    path('iplist-autocomplete', views_autocomplete.IpListAutocomplete.as_view(), name='iplist-autocomplete',),
]
