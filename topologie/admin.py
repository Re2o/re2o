
from django.contrib import admin

from .models import Port, Room, Link

class PortAdmin(admin.ModelAdmin):
    list_display = ('building','switch', 'port','details')

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room','details')

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room','details')

class LinkAdmin(admin.ModelAdmin):
    list_display = ('port', 'room','details')

admin.site.register(Port, PortAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Link, LinkAdmin)
