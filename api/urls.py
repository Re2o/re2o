# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
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

"""Defines the URLs of the API

A custom router is used to register all the routes. That allows to register
all the URL patterns from the viewsets as a standard router but, the views
can also be register. That way a complete API root page presenting all URLs
can be generated automatically.
"""

from django.conf.urls import url, include

from . import views
from .routers import AllViewsRouter


router = AllViewsRouter()
# COTISATIONS
router.register_viewset(r'cotisations/facture', views.FactureViewSet)
router.register_viewset(r'cotisations/vente', views.VenteViewSet)
router.register_viewset(r'cotisations/article', views.ArticleViewSet)
router.register_viewset(r'cotisations/banque', views.BanqueViewSet)
router.register_viewset(r'cotisations/paiement', views.PaiementViewSet)
router.register_viewset(r'cotisations/cotisation', views.CotisationViewSet)
# MACHINES
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
# PREFERENCES
router.register_view(r'preferences/optionaluser', views.OptionalUserView),
router.register_view(r'preferences/optionalmachine', views.OptionalMachineView),
router.register_view(r'preferences/optionaltopologie', views.OptionalTopologieView),
router.register_view(r'preferences/generaloption', views.GeneralOptionView),
router.register_viewset(r'preferences/service', views.HomeServiceViewSet, base_name='homeservice'),
router.register_view(r'preferences/assooption', views.AssoOptionView),
router.register_view(r'preferences/homeoption', views.HomeOptionView),
router.register_view(r'preferences/mailmessageoption', views.MailMessageOptionView),
# TOPOLOGIE
router.register_viewset(r'topologie/stack', views.StackViewSet)
router.register_viewset(r'topologie/acesspoint', views.AccessPointViewSet)
router.register_viewset(r'topologie/switch', views.SwitchViewSet)
router.register_viewset(r'topologie/server', views.ServerViewSet)
router.register_viewset(r'topologie/modelswitch', views.ModelSwitchViewSet)
router.register_viewset(r'topologie/constructorswitch', views.ConstructorSwitchViewSet)
router.register_viewset(r'topologie/switchbay', views.SwitchBayViewSet)
router.register_viewset(r'topologie/building', views.BuildingViewSet)
router.register_viewset(r'topologie/switchport', views.SwitchPortViewSet, base_name='switchport')
router.register_viewset(r'topologie/portprofile', views.PortProfileViewSet, base_name='portprofile')
router.register_viewset(r'topologie/room', views.RoomViewSet)
router.register(r'topologie/portprofile', views.PortProfileViewSet)
# USERS
router.register_viewset(r'users/user', views.UserViewSet)
router.register_viewset(r'users/homecreation', views.HomeCreationViewSet)
router.register_viewset(r'users/club', views.ClubViewSet)
router.register_viewset(r'users/adherent', views.AdherentViewSet)
router.register_viewset(r'users/serviceuser', views.ServiceUserViewSet)
router.register_viewset(r'users/school', views.SchoolViewSet)
router.register_viewset(r'users/listright', views.ListRightViewSet)
router.register_viewset(r'users/shell', views.ShellViewSet, base_name='shell')
router.register_viewset(r'users/ban', views.BanViewSet)
router.register_viewset(r'users/whitelist', views.WhitelistViewSet)
router.register_viewset(r'users/emailaddress', views.EMailAddressViewSet)
# SERVICE REGEN
router.register_viewset(r'services/regen', views.ServiceRegenViewSet, base_name='serviceregen')
# DHCP
router.register_view(r'dhcp/hostmacip', views.HostMacIpView),
# LOCAL EMAILS
router.register_view(r'localemail/users', views.LocalEmailUsersView),
# Firewall
router.register_view(r'firewall/subnet-ports', views.SubnetPortsOpenView),
router.register_view(r'firewall/interface-ports', views.InterfacePortsOpenView),
# Switches config
router.register_view(r'switchs/ports-config', views.SwitchPortView),
router.register_view(r'switchs/role', views.RoleView),
# DNS
router.register_view(r'dns/zones', views.DNSZonesView),
router.register_view(r'dns/reverse-zones', views.DNSReverseZonesView),
# MAILING
router.register_view(r'mailing/standard', views.StandardMailingView),
router.register_view(r'mailing/club', views.ClubMailingView),
# TOKEN AUTHENTICATION
router.register_view(r'token-auth', views.ObtainExpiringAuthToken)


urlpatterns = [
    url(r'^', include(router.urls)),
]
