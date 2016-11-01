from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import IpType, Machine, MachineType, Alias, IpList, Interface, Extension

class MachineAdmin(VersionAdmin):
    list_display = ('user','name','active')

class IpTypeAdmin(VersionAdmin):
    list_display = ('type','extension','need_infra')

class MachineTypeAdmin(VersionAdmin):
    list_display = ('type','ip_type')


class ExtensionAdmin(VersionAdmin):
    list_display = ('name',)

class IpListAdmin(VersionAdmin):
    list_display = ('ipv4','ip_type')

class InterfaceAdmin(VersionAdmin):
    list_display = ('machine','type','dns','mac_address','ipv4','details')

class AliasAdmin(VersionAdmin):
    list_display = ('interface_parent', 'alias')

admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(IpType, IpTypeAdmin)
admin.site.register(Extension, ExtensionAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Alias, AliasAdmin)
