# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
Admin views basic definition, include basic definition of admin view.

Except for Admin edition and creation of users and services users;
with AdherentAdmin, ClubAdmin and ServiceUserAdmin.
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from reversion.admin import VersionAdmin

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
    LdapUserGroup,
)
from .forms import (
    UserAdminForm,
    ServiceUserAdminForm,
)


class LdapUserAdmin(admin.ModelAdmin):
    """LdapUser Admin view. Can't change password, manage
    by User General model.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """
    list_display = ("name", "uidNumber", "login_shell")
    exclude = ("user_password", "sambat_nt_password")
    search_fields = ("name",)


class LdapServiceUserAdmin(admin.ModelAdmin):
    """LdapServiceUser Admin view. Can't change password, manage
    by User General model.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    list_display = ("name",)
    exclude = ("user_password",)
    search_fields = ("name",)


class LdapUserGroupAdmin(admin.ModelAdmin):
    """LdapUserGroup Admin view.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    list_display = ("name", "members", "gid")
    search_fields = ("name",)


class LdapServiceUserGroupAdmin(admin.ModelAdmin):
    """LdapServiceUserGroup Admin view.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    list_display = ("name",)
    search_fields = ("name",)


class SchoolAdmin(VersionAdmin):
    """School Admin view and management.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    pass


class ListRightAdmin(VersionAdmin):
    """ListRight and groups Admin view and management.
    Even if it is possible, gid should NOT be changed
    as it is the ldap primary key.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    list_display = ("unix_name",)


class ListShellAdmin(VersionAdmin):
    """Users Shell Admin view and management.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    pass


class RequestAdmin(admin.ModelAdmin):
    """User Request Admin view and management, for
    change password and email validation.

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    list_display = ("user", "type", "created_at", "expires_at")


class BanAdmin(VersionAdmin):
    """Ban Admin view and management, for
    User Ban

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    pass


class EMailAddressAdmin(VersionAdmin):
    """EmailAddress Admin view and management, for
    auxiliary and local email addresses

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    pass


class WhitelistAdmin(VersionAdmin):
    """Whitelist Admin view and management, for
    free access whitelisted users

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    pass


class AdherentAdmin(VersionAdmin, BaseUserAdmin):
    """Adherent Admin view and management, for
    Adherent fields : password, pseudo, etc, admin can
    edit all fields on user instance.
    Inherit from django BaseUserAdmin

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    # The forms to add and change user instances

    add_form = UserAdminForm
    form = UserAdminForm

    list_display = (
        "pseudo",
        "name",
        "surname",
        "email",
        "local_email_redirect",
        "local_email_enabled",
        "school",
        "shell",
    )
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("pseudo",)}),
        (
            "Personal info",
            {"fields": ("surname", "name", "email", "school", "shell", "uid_number", "profile_image", "password1", "password2")},
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "pseudo",
                    "surname",
                    "name",
                    "email",
                    "school",
                    "password1",
                    "password2",
                    "profile_image",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("pseudo", "surname", "name")
    ordering = ("pseudo",)
    filter_horizontal = ()


class ClubAdmin(VersionAdmin, BaseUserAdmin):
    """Club Admin view and management, for
    Club fields : password, pseudo, etc, admin can
    edit all fields on user instance.
    Inherit from django BaseUserAdmin

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """
    # The forms to add and change user instances
    add_form = UserAdminForm
    form = UserAdminForm

    list_display = (
        "pseudo",
        "surname",
        "email",
        "local_email_redirect",
        "local_email_enabled",
        "school",
        "shell",
    )
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("pseudo",)}),
        (
            "Personal info",
            {"fields": ("surname", "email", "school", "shell", "uid_number", "profile_image", "password1", "password2")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "pseudo",
                    "surname",
                    "email",
                    "school",
                    "password1",
                    "password2",
                    "profile_image",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("pseudo", "surname")
    ordering = ("pseudo",)
    filter_horizontal = ()


class ServiceUserAdmin(VersionAdmin, BaseUserAdmin):
    """ServiceUser Admin view and management, for
    User fields : password, pseudo, etc, admin can
    edit all fields on user instance.
    Inherit from django BaseUserAdmin

    Parameters:
        Django ModelAdmin: Apply on django ModelAdmin

    """

    # The forms to add and change user instances
    form = ServiceUserAdminForm
    add_form = ServiceUserAdminForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("pseudo", "access_group")
    list_filter = ()
    fieldsets = ((None, {"fields": ("pseudo", "access_group", "comment", "password1", "password2")}),)
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("pseudo", "password1", "password2")}),
    )
    search_fields = ("pseudo",)
    ordering = ("pseudo",)
    filter_horizontal = ()


admin.site.register(Adherent, AdherentAdmin)
admin.site.register(Club, ClubAdmin)
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
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
