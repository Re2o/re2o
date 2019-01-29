# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019 Arthur Grisel-Davy
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

from django.conf.urls import url, include
from . import views
from api.routers import AllViewsRouter

def add_to_router(router):
    router.register_viewset(r'machines/machine', views.MachineViewSet)
    router.register_viewset(r'machines/machinetype', views.MachineTypeViewSet)
    router.register_viewset(r'machines/iptype', views.IpTypeViewSet)
    router.register_viewset(r'machines/vlan', views.VlanViewSet)
    router.register_viewset(r'machines/nas', views.NasViewSet)
    router.register_viewset(r'machines/soa', views.SOAViewSet)
    router.register_viewset(r'machines/extension', views.ExtensionViewSet)
    router.register_viewset(r'machines/mx', views.MxViewSet)
    router.register_viewset(r'machines/ns', views.NsViewSet)
    router.register_viewset(r'machines/txt', views.TxtViewSet)
    router.register_viewset(r'machines/dname', views.DNameViewSet)
    router.register_viewset(r'machines/srv', views.SrvViewSet)
    router.register_viewset(r'machines/sshfp', views.SshFpViewSet)
    router.register_viewset(r'machines/interface', views.InterfaceViewSet)
    router.register_viewset(r'machines/ipv6list', views.Ipv6ListViewSet)
    router.register_viewset(r'machines/domain', views.DomainViewSet)
    router.register_viewset(r'machines/iplist', views.IpListViewSet)
    router.register_viewset(r'machines/service', views.ServiceViewSet)
    router.register_viewset(r'machines/servicelink', views.ServiceLinkViewSet, base_name='servicelink')
    router.register_viewset(r'machines/ouvertureportlist', views.OuverturePortListViewSet)
    router.register_viewset(r'machines/ouvertureport', views.OuverturePortViewSet)
    router.register_viewset(r'machines/role', views.RoleViewSet)
