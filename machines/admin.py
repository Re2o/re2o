from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Machine, MachineType, IpList, Interface, Extension

class MachineAdmin(VersionAdmin):
    list_display = ('user','name','active')

class MachineTypeAdmin(VersionAdmin):
    list_display = ('type','extension')

class ExtensionAdmin(VersionAdmin):
    list_display = ('name',)

class IpListAdmin(VersionAdmin):
    list_display = ('ipv4',)

class InterfaceAdmin(VersionAdmin):
    list_display = ('machine','type','dns','mac_address','ipv4','details')

admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(Extension, ExtensionAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
