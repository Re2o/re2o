from django.contrib import admin

from .models import User, School, Right, ListRight, Ban, Whitelist

class UserAdmin(admin.ModelAdmin):
    list_display = ('name','surname','pseudo','room','email', 'school', 'state')

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ListRightAdmin(admin.ModelAdmin):
    list_display = ('listright',)

class RightAdmin(admin.ModelAdmin):
    list_display = ('user', 'right')

class BanAdmin(admin.ModelAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')

class WhitelistAdmin(admin.ModelAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')

admin.site.register(User, UserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Right, RightAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
