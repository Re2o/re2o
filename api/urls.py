# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Mael Kervella
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
"""api.urls

Urls de l'api, pointant vers les fonctions de views
"""

from __future__ import unicode_literals

from django.conf.urls import url, include

from .routers import AllViewsRouter
from . import views

router = AllViewsRouter()
# COTISATIONS APP
router.register_viewset(r'cotisations/factures', views.FactureViewSet)
router.register_viewset(r'cotisations/ventes', views.VenteViewSet)
router.register_viewset(r'cotisations/articles', views.ArticleViewSet)
router.register_viewset(r'cotisations/banques', views.BanqueViewSet)
router.register_viewset(r'cotisations/paiements', views.PaiementViewSet)
router.register_viewset(r'cotisations/cotisations', views.CotisationViewSet)
# MACHINES APP
router.register_viewset(r'machines/machines', views.MachineViewSet)
router.register_viewset(r'machines/machinetypes', views.MachineTypeViewSet)
router.register_viewset(r'machines/iptypes', views.IpTypeViewSet)
router.register_viewset(r'machines/vlans', views.VlanViewSet)
router.register_viewset(r'machines/nas', views.NasViewSet)
router.register_viewset(r'machines/soa', views.SOAViewSet)
router.register_viewset(r'machines/extensions', views.ExtensionViewSet)
router.register_viewset(r'machines/mx', views.MxViewSet)
router.register_viewset(r'machines/ns', views.NsViewSet)
router.register_viewset(r'machines/txt', views.TxtViewSet)
router.register_viewset(r'machines/srv', views.SrvViewSet)
router.register_viewset(r'machines/interfaces', views.InterfaceViewSet)
router.register_viewset(r'machines/ipv6lists', views.Ipv6ListViewSet)
router.register_viewset(r'machines/domains', views.DomainViewSet)
router.register_viewset(r'machines/iplists', views.IpListViewSet)
router.register_viewset(r'machines/services', views.ServiceViewSet)
router.register_viewset(r'machines/servicelinks', views.ServiceLinkViewSet, base_name='servicelink')
router.register_viewset(r'machines/ouvertureportlists', views.OuverturePortListViewSet)
router.register_viewset(r'machines/ouvertureports', views.OuverturePortViewSet)
# PREFERENCES APP
router.register_viewset(r'preferences/service', views.ServiceViewSet),
router.register_view(r'preferences/optionaluser', views.OptionalUserView),
router.register_view(r'preferences/optionalmachine', views.OptionalMachineView),
router.register_view(r'preferences/optionaltopologie', views.OptionalTopologieView),
router.register_view(r'preferences/generaloption', views.GeneralOptionView),
router.register_view(r'preferences/assooption', views.AssoOptionView),
router.register_view(r'preferences/homeoption', views.HomeOptionView),
router.register_view(r'preferences/mailmessageoption', views.MailMessageOptionView),
# TOPOLOGIE APP
router.register_viewset(r'topologie/stack', views.StackViewSet)
router.register_viewset(r'topologie/acesspoint', views.AccessPointViewSet)
router.register_viewset(r'topologie/switch', views.SwitchViewSet)
router.register_viewset(r'topologie/modelswitch', views.ModelSwitchViewSet)
router.register_viewset(r'topologie/constructorswitch', views.ConstructorSwitchViewSet)
router.register_viewset(r'topologie/switchbay', views.SwitchBayViewSet)
router.register_viewset(r'topologie/building', views.BuildingViewSet)
router.register_viewset(r'topologie/switchport', views.SwitchPortViewSet, base_name='switchport')
router.register_viewset(r'topologie/room', views.RoomViewSet)
# USERS APP
router.register_viewset(r'users/users', views.UserViewSet)
router.register_viewset(r'users/clubs', views.ClubViewSet)
router.register_viewset(r'users/adherents', views.AdherentViewSet)
router.register_viewset(r'users/serviceusers', views.ServiceUserViewSet)
router.register_viewset(r'users/schools', views.SchoolViewSet)
router.register_viewset(r'users/listrights', views.ListRightViewSet)
router.register_viewset(r'users/shells', views.ShellViewSet, base_name='shell')
router.register_viewset(r'users/bans', views.BanViewSet)
router.register_viewset(r'users/whitelists', views.WhitelistViewSet)
# SERVICES REGEN
router.register_viewset(r'services/regen', views.ServiceRegenViewSet, base_name='serviceregen')
# DHCP
router.register_view(r'dhcp/hostmacip', views.HostMacIpView),
# DNS
router.register_view(r'dns/zones', views.DNSZonesView),
# MAILING
router.register_view(r'mailing/standard', views.StandardMailingView),
router.register_view(r'mailing/club', views.ClubMailingView),
# TOKEN-AUTH
router.register_view(r'token-auth', views.ObtainExpiringAuthToken)


urlpatterns = [
    url(r'^', include(router.urls)),
]
