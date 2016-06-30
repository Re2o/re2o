from django.contrib import admin

from .models import User, School

class UserAdmin(admin.ModelAdmin):
    list_display = ('name','surname','pseudo','email', 'school', 'state')

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(School, SchoolAdmin)
