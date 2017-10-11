# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from reversion.admin import VersionAdmin

from .models import User, ServiceUser, School, Right, ListRight, ListShell, BanType, Ban, Whitelist, Request, LdapUser, LdapServiceUser, LdapServiceUserGroup, LdapUserGroup
from .forms import UserChangeForm, UserCreationForm, ServiceUserChangeForm, ServiceUserCreationForm


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'surname',
        'pseudo',
        'room',
        'email',
        'school',
        'shell',
        'state'
    )
    search_fields = ('name','surname','pseudo','room')


class LdapUserAdmin(admin.ModelAdmin):
    list_display = ('name','uidNumber','login_shell')
    exclude = ('user_password','sambat_nt_password')
    search_fields = ('name',)

class LdapServiceUserAdmin(admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('user_password',)
    search_fields = ('name',)

class LdapUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name','members','gid')
    search_fields = ('name',)

class LdapServiceUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class SchoolAdmin(VersionAdmin):
    list_display = ('name',)

class ListRightAdmin(VersionAdmin):
    list_display = ('listright',)

class ListShellAdmin(VersionAdmin):
    list_display = ('shell',)

class RightAdmin(VersionAdmin):
    list_display = ('user', 'right')

class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at', 'expires_at')

class BanAdmin(VersionAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')

class BanTypeAdmin(VersionAdmin):
    list_display = ('name', 'description')

class WhitelistAdmin(VersionAdmin):
    list_display = ('user', 'raison', 'date_start', 'date_end')


class UserAdmin(VersionAdmin, BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('pseudo', 'name', 'surname', 'email', 'school', 'is_admin', 'shell')
    list_display = ('pseudo',)
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'email', 'school','shell', 'uid_number')}),
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

class ServiceUserAdmin(VersionAdmin, BaseUserAdmin):
    # The forms to add and change user instances
    form = ServiceUserChangeForm
    add_form = ServiceUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('pseudo', 'access_group')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password', 'access_group')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('pseudo', 'password1', 'password2')}
        ),
    )
    search_fields = ('pseudo',)
    ordering = ('pseudo',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(LdapUserGroup, LdapUserGroupAdmin)
admin.site.register(LdapServiceUser, LdapServiceUserAdmin)
admin.site.register(LdapServiceUserGroup, LdapServiceUserGroupAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Right, RightAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(ListShell, ListShellAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(BanType, BanTypeAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.unregister(ServiceUser)
admin.site.register(User, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
