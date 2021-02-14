# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

from . import views

urls_viewset = [
    (r"machines/machine", views.MachineViewSet, None),
    (r"machines/machinetype", views.MachineTypeViewSet, None),
    (r"machines/iptype", views.IpTypeViewSet, None),
    (r"machines/vlan", views.VlanViewSet, None),
    (r"machines/nas", views.NasViewSet, None),
    (r"machines/soa", views.SOAViewSet, None),
    (r"machines/extension", views.ExtensionViewSet, None),
    (r"machines/mx", views.MxViewSet, None),
    (r"machines/ns", views.NsViewSet, None),
    (r"machines/txt", views.TxtViewSet, None),
    (r"machines/dname", views.DNameViewSet, None),
    (r"machines/srv", views.SrvViewSet, None),
    (r"machines/sshfp", views.SshFpViewSet, None),
    (r"machines/interface", views.InterfaceViewSet, None),
    (r"machines/ipv6list", views.Ipv6ListViewSet, None),
    (r"machines/domain", views.DomainViewSet, None),
    (r"machines/iplist", views.IpListViewSet, None),
    (r"machines/service", views.ServiceViewSet, None),
    (r"machines/servicelink", views.ServiceLinkViewSet, "servicelink"),
    (r"machines/ouvertureportlist", views.OuverturePortListViewSet, None),
    (r"machines/ouvertureport", views.OuverturePortViewSet, None),
    (r"machines/role", views.RoleViewSet, None),
    (r"machines/services-regen", views.ServiceRegenViewSet, "serviceregen"),
    # Deprecated
    (r"services/regen", views.ServiceRegenViewSet, "serviceregen"),
]

urls_view = [
    (r"machines/hostmacip", views.HostMacIpView),
    (r"machines/firewall-subnet-ports", views.SubnetPortsOpenView),
    (r"machines/firewall-interface-ports", views.InterfacePortsOpenView),
    (r"machines/dns-zones", views.DNSZonesView),
    (r"machines/dns-reverse-zones", views.DNSReverseZonesView),
    # Deprecated
    (r"dhcp/hostmacip", views.HostMacIpView),
    (r"firewall/subnet-ports", views.SubnetPortsOpenView),
    (r"firewall/interface-ports", views.InterfacePortsOpenView),
    (r"dns/zones", views.DNSZonesView),
    (r"dns/reverse-zones", views.DNSReverseZonesView),
]
