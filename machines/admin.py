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
    list_display = ('zone', 'interface')

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
