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
"""machines.admin
The objects, fields and datastructures visible in the Django admin view
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (SOA, DName, Domain, Extension, Interface, IpList, IpType,
                     Ipv6List, Machine, MachineType, Mx, Nas, Ns,
                     OuverturePort, OuverturePortList, Role, Service, Srv,
                     SshFp, Txt, Vlan)


class MachineAdmin(VersionAdmin):
    """ Admin view of a Machine object """

    pass


class Ipv6ListAdmin(VersionAdmin):
    """ Admin view of a Ipv6List object """

    pass


class IpTypeAdmin(VersionAdmin):
    """ Admin view of a IpType object """

    pass


class MachineTypeAdmin(VersionAdmin):
    """ Admin view of a MachineType object """

    pass


class VlanAdmin(VersionAdmin):
    """ Admin view of a Vlan object """

    pass


class ExtensionAdmin(VersionAdmin):
    """ Admin view of a Extension object """

    pass


class SOAAdmin(VersionAdmin):
    """ Admin view of a SOA object """

    pass


class MxAdmin(VersionAdmin):
    """ Admin view of a MX object """

    pass


class NsAdmin(VersionAdmin):
    """ Admin view of a NS object """

    pass


class TxtAdmin(VersionAdmin):
    """ Admin view of a TXT object """

    pass


class DNameAdmin(VersionAdmin):
    """ Admin view of a DName object """

    pass


class SrvAdmin(VersionAdmin):
    """ Admin view of a SRV object """

    pass


class SshFpAdmin(VersionAdmin):
    """ Admin view of a SSHFP object """

    pass


class NasAdmin(VersionAdmin):
    """ Admin view of a Nas object """

    pass


class IpListAdmin(VersionAdmin):
    """ Admin view of a Ipv4List object """

    pass


class OuverturePortAdmin(VersionAdmin):
    """ Admin view of a OuverturePort object """

    pass


class OuverturePortListAdmin(VersionAdmin):
    """ Admin view of a OuverturePortList object """

    pass


class InterfaceAdmin(VersionAdmin):
    """ Admin view of a Interface object """

    list_display = ("machine", "machine_type", "mac_address", "ipv4", "details")


class DomainAdmin(VersionAdmin):
    """ Admin view of a Domain object """

    list_display = ("interface_parent", "name", "extension", "cname")


class ServiceAdmin(VersionAdmin):
    """ Admin view of a ServiceAdmin object """

    list_display = ("service_type", "min_time_regen", "regular_time_regen")


class RoleAdmin(VersionAdmin):
    """ Admin view of a RoleAdmin object """

    pass


admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(IpType, IpTypeAdmin)
admin.site.register(Extension, ExtensionAdmin)
admin.site.register(SOA, SOAAdmin)
admin.site.register(Mx, MxAdmin)
admin.site.register(Ns, NsAdmin)
admin.site.register(Txt, TxtAdmin)
admin.site.register(DName, DNameAdmin)
admin.site.register(Srv, SrvAdmin)
admin.site.register(SshFp, SshFpAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Vlan, VlanAdmin)
admin.site.register(Ipv6List, Ipv6ListAdmin)
admin.site.register(Nas, NasAdmin)
admin.site.register(OuverturePort, OuverturePortAdmin)
admin.site.register(OuverturePortList, OuverturePortListAdmin)
