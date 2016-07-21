
from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Port, Room, Switch

class SwitchAdmin(VersionAdmin):
    list_display = ('building','number','details')

class PortAdmin(VersionAdmin):
    list_display = ('switch', 'port','room','machine_interface','details')

class RoomAdmin(VersionAdmin):
    list_display = ('name','details')

admin.site.register(Port, PortAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Switch, SwitchAdmin)
