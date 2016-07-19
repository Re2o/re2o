
from django.contrib import admin

from .models import Port, Room, Switch

class SwitchAdmin(admin.ModelAdmin):
    list_display = ('building','number','details')

class PortAdmin(admin.ModelAdmin):
    list_display = ('switch', 'port','room','machine_interface','details')

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name','details')

admin.site.register(Port, PortAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Switch, SwitchAdmin)
