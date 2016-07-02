from django.contrib import admin

from .models import User, School, Right, ListRight

class UserAdmin(admin.ModelAdmin):
    list_display = ('name','surname','pseudo','email', 'school', 'state')

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ListRightAdmin(admin.ModelAdmin):
    list_display = ('listright',)

class RightAdmin(admin.ModelAdmin):
    list_display = ('user', 'right')

admin.site.register(User, UserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Right, RightAdmin)
admin.site.register(ListRight, ListRightAdmin)
