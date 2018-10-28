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
"""
Admin views definition
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from reversion.admin import VersionAdmin

from .forms import (
    UserChangeForm,
    UserCreationForm,
    ServiceUserChangeForm,
    ServiceUserCreationForm
)
from .models import (
    User,
    EMailAddress,
    ServiceUser,
    School,
    ListRight,
    ListShell,
    Adherent,
    Club,
    Ban,
    Whitelist,
    Request,
    LdapUser,
    LdapServiceUser,
    LdapServiceUserGroup,
    LdapUserGroup
)


class LdapUserAdmin(admin.ModelAdmin):
    """LDAP users admin page"""
    list_display = ('name', 'uidNumber', 'login_shell')
    exclude = ('user_password', 'sambat_nt_password')
    search_fields = ('name',)


class LdapServiceUserAdmin(admin.ModelAdmin):
    """LDAP service users admin page"""
    list_display = ('name',)
    exclude = ('user_password',)
    search_fields = ('name',)


class LdapUserGroupAdmin(admin.ModelAdmin):
    """LDAP user groups admin page"""
    list_display = ('name', 'members', 'gid')
    search_fields = ('name',)


class LdapServiceUserGroupAdmin(admin.ModelAdmin):
    """LDAP service user groups admin page"""
    list_display = ('name',)
    search_fields = ('name',)


class SchoolAdmin(VersionAdmin):
    """Schools admin page (with revisions)"""
    pass


class ListRightAdmin(VersionAdmin):
    """Existing right admin page (with revisions)

    Can not edit gid because it is a primary key for LDAP
    """
    list_display = ('unix_name',)


class ListShellAdmin(VersionAdmin):
    """Shells admin page (with revisions)"""
    pass


class RequestAdmin(admin.ModelAdmin):
    """User request admin page

    It contains tickets for password reinitialisation.
    """
    list_display = ('user', 'type', 'created_at', 'expires_at')


class BanAdmin(VersionAdmin):
    """Banned user admin page (with revisions)"""
    pass


class EMailAddressAdmin(VersionAdmin):
    """Mail aliases admin page (with revisions)"""
    pass


class WhitelistAdmin(VersionAdmin):
    """Whitelist admin page"""
    pass


class UserAdmin(VersionAdmin, BaseUserAdmin):
    """User admin page (with revisions, based on Django user admin page)"""

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'pseudo',
        'surname',
        'email',
        'local_email_redirect',
        'local_email_enabled',
        'school',
        'is_admin',
        'shell'
    )
    # Need to reset the settings from BaseUserAdmin
    # They are using fields we don't use like 'is_staff'
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password')}),
        (
            'Personal info',
            {
                'fields':
                    ('surname', 'email', 'school', 'shell', 'uid_number')
            }
        ),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'pseudo',
                    'surname',
                    'email',
                    'school',
                    'is_admin',
                    'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ('pseudo', 'surname')
    ordering = ('pseudo',)
    filter_horizontal = ()


class ServiceUserAdmin(VersionAdmin, BaseUserAdmin):
    """Service user admin page (with revisions, based on Django user admin page)"""

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
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('pseudo', 'password1', 'password2')
            }
        ),
    )
    search_fields = ('pseudo',)
    ordering = ('pseudo',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Adherent, UserAdmin)
admin.site.register(Club, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(LdapUserGroup, LdapUserGroupAdmin)
admin.site.register(LdapServiceUser, LdapServiceUserAdmin)
admin.site.register(LdapServiceUserGroup, LdapServiceUserGroupAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(ListShell, ListShellAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(EMailAddress, EMailAddressAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin and ServiceUser (replacing Django default ones)...
admin.site.unregister(User)
admin.site.unregister(ServiceUser)
admin.site.register(User, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
