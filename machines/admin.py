from django.contrib import admin

from .models import Machine, MachineType

class MachineAdmin(admin.ModelAdmin):
    list_display = ('user','type')

class MachineTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)

admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)
