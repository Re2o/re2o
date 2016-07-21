from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from reversion.admin import VersionAdmin

from .models import User, School, Right, ListRight, Ban, Whitelist, Request
from .forms import UserChangeForm, UserCreationForm


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'surname',
        'pseudo',
        'room',
        'email',
        'school',
        'state'
    )


class SchoolAdmin(VersionAdmin):
    list_display = ('name',)


class ListRightAdmin(VersionAdmin):
    list_display = ('listright',)


class RightAdmin(admin.ModelAdmin):
    list_display = ('user', 'right')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at', 'expires_at')

class BanAdmin(VersionAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')


class WhitelistAdmin(VersionAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')


class UserAdmin(VersionAdmin, BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('pseudo', 'name', 'surname', 'email', 'school', 'is_admin')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'email', 'school')}),
        ('Permissions', {'fields': ('is_admin', )}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('pseudo', 'name', 'surname', 'email', 'school', 'is_admin', 'password1', 'password2')}
        ),
    )
    search_fields = ('pseudo',)
    ordering = ('pseudo',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Right, RightAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
