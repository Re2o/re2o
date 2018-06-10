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
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# COTISATIONS APP
router.register(r'cotisations/factures', views.FactureViewSet)
router.register(r'cotisations/ventes', views.VenteViewSet)
router.register(r'cotisations/articles', views.ArticleViewSet)
router.register(r'cotisations/banques', views.BanqueViewSet)
router.register(r'cotisations/paiements', views.PaiementViewSet)
router.register(r'cotisations/cotisations', views.CotisationViewSet)
# MACHINES APP
router.register(r'machines/machines', views.MachineViewSet)
router.register(r'machines/machinetypes', views.MachineTypeViewSet)
router.register(r'machines/iptypes', views.IpTypeViewSet)
router.register(r'machines/vlans', views.VlanViewSet)
router.register(r'machines/nas', views.NasViewSet)
router.register(r'machines/soa', views.SOAViewSet)
router.register(r'machines/extensions', views.ExtensionViewSet)
router.register(r'machines/mx', views.MxViewSet)
router.register(r'machines/ns', views.NsViewSet)
router.register(r'machines/txt', views.TxtViewSet)
router.register(r'machines/srv', views.SrvViewSet)
router.register(r'machines/interfaces', views.InterfaceViewSet)
router.register(r'machines/ipv6lists', views.Ipv6ListViewSet)
router.register(r'machines/domains', views.DomainViewSet)
router.register(r'machines/iplists', views.IpListViewSet)
router.register(r'machines/services', views.ServiceViewSet)
router.register(r'machines/servicelinks', views.ServiceLinkViewSet, base_name='servicelink')
router.register(r'machines/ouvertureportlists', views.OuverturePortListViewSet)
router.register(r'machines/ouvertureports', views.OuverturePortViewSet)
# PREFERENCES APP
#router.register(r'preferences/optionaluser', views.OptionalUserSerializer)
#router.register(r'preferences/optionalmachine', views.OptionalMachineSerializer)
#router.register(r'preferences/optionaltopologie', views.OptionalTopologieSerializer)
#router.register(r'preferences/generaloption', views.GeneralOptionSerializer)
#router.register(r'preferences/serviceoption', views.ServiceOptionSerializer)
#router.register(r'preferences/assooption', views.AssoOptionSerializer)
#router.register(r'preferences/homeoption', views.HomeOptionSerializer)
#router.register(r'preferences/mailmessageoption', views.MailMessageOptionSerializer)
# TOPOLOGIE APP
router.register(r'topologie/stack', views.StackViewSet)
router.register(r'topologie/acesspoint', views.AccessPointViewSet)
router.register(r'topologie/switch', views.SwitchViewSet)
router.register(r'topologie/modelswitch', views.ModelSwitchViewSet)
router.register(r'topologie/constructorswitch', views.ConstructorSwitchViewSet)
router.register(r'topologie/switchbay', views.SwitchBayViewSet)
router.register(r'topologie/building', views.BuildingViewSet)
router.register(r'topologie/switchport', views.SwitchPortViewSet, base_name='switchport')
router.register(r'topologie/room', views.RoomViewSet)
# USERS APP
router.register(r'users/users', views.UserViewSet)
router.register(r'users/clubs', views.ClubViewSet)
router.register(r'users/adherents', views.AdherentViewSet)
router.register(r'users/serviceusers', views.ServiceUserViewSet)
router.register(r'users/schools', views.SchoolViewSet)
router.register(r'users/listrights', views.ListRightViewSet)
router.register(r'users/shells', views.ShellViewSet, base_name='shell')
router.register(r'users/bans', views.BanViewSet)
router.register(r'users/whitelists', views.WhitelistViewSet)
# SERVICES REGEN
router.register(r'services/regen', views.ServiceRegenViewSet, base_name='serviceregen')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^dhcp/hostmacip', views.HostMacIpView.as_view()),
    url(r'^dns/zones', views.DNSZonesView.as_view()),
    url(r'^mailing/standard', views.StandardMailingView.as_view()),
    url(r'^mailing/club', views.ClubMailingView.as_view()),
    url(r'^token-auth', views.ObtainExpiringAuthToken.as_view())
]
