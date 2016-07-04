from django.contrib import admin

from .models import Machine, MachineType, IpList, Interface

class MachineAdmin(admin.ModelAdmin):
    list_display = ('user','name','type')

class MachineTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)

class IpListAdmin(admin.ModelAdmin):
    list_display = ('ipv4',)

class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('machine','dns','mac_address','ipv4','details')

admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
