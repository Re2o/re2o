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

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import IpType, Machine, MachineType, Domain, IpList, Interface, Extension, Mx, Ns

class MachineAdmin(VersionAdmin):
    list_display = ('user','name','active')

class IpTypeAdmin(VersionAdmin):
    list_display = ('type','extension','need_infra','domaine_ip','domaine_range')

class MachineTypeAdmin(VersionAdmin):
    list_display = ('type','ip_type')


class ExtensionAdmin(VersionAdmin):
    list_display = ('name','origin')

class MxAdmin(VersionAdmin):
    list_display = ('zone', 'priority', 'name')

class NsAdmin(VersionAdmin):
    list_display = ('zone', 'ns')

class IpListAdmin(VersionAdmin):
    list_display = ('ipv4','ip_type')

class InterfaceAdmin(VersionAdmin):
    list_display = ('machine','type','mac_address','ipv4','details')

class DomainAdmin(VersionAdmin):
    list_display = ('interface_parent', 'name', 'extension', 'cname')

admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(IpType, IpTypeAdmin)
admin.site.register(Extension, ExtensionAdmin)
admin.site.register(Mx, MxAdmin)
admin.site.register(Ns, NsAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Domain, DomainAdmin)
