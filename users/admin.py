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
Definition des vues pour les admin. Classique, sauf pour users,
où on fait appel à UserChange et ServiceUserChange, forms custom
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
    ServiceUserChangeForm,
    ServiceUserCreationForm,
)


class LdapUserAdmin(admin.ModelAdmin):
    """Administration du ldapuser"""

    list_display = ("name", "uidNumber", "login_shell")
    exclude = ("user_password", "sambat_nt_password")
    search_fields = ("name",)


class LdapServiceUserAdmin(admin.ModelAdmin):
    """Administration du ldapserviceuser"""

    list_display = ("name",)
    exclude = ("user_password",)
    search_fields = ("name",)


class LdapUserGroupAdmin(admin.ModelAdmin):
    """Administration du ldapusergroupe"""

    list_display = ("name", "members", "gid")
    search_fields = ("name",)


class LdapServiceUserGroupAdmin(admin.ModelAdmin):
    """Administration du ldap serviceusergroup"""

    list_display = ("name",)
    search_fields = ("name",)


class SchoolAdmin(VersionAdmin):
    """Administration, gestion des écoles"""

    pass


class ListRightAdmin(VersionAdmin):
    """Gestion de la liste des droits existants
    Ne permet pas l'edition du gid (primarykey pour ldap)"""

    list_display = ("unix_name",)


class ListShellAdmin(VersionAdmin):
    """Gestion de la liste des shells coté admin"""

    pass


class RequestAdmin(admin.ModelAdmin):
    """Gestion des request objet, ticket pour lien de reinit mot de passe"""

    list_display = ("user", "type", "created_at", "expires_at")


class BanAdmin(VersionAdmin):
    """Gestion des bannissements"""

    pass


class EMailAddressAdmin(VersionAdmin):
    """Gestion des alias mail"""

    pass


class WhitelistAdmin(VersionAdmin):
    """Gestion des whitelist"""

    pass


class AdherentAdmin(VersionAdmin, BaseUserAdmin):
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
    """Gestion d'un service user admin : champs personnels,
    mot de passe; etc"""

    # The forms to add and change user instances
    form = ServiceUserChangeForm
    add_form = ServiceUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ("pseudo", "access_group")
    list_filter = ()
    fieldsets = ((None, {"fields": ("pseudo", "password", "access_group")}),)
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
# Now register the new UserAdmin...
admin.site.unregister(ServiceUser)
admin.site.register(ServiceUser, ServiceUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
