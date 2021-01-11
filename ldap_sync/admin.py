from django.contrib import admin

from .models import (
    LdapUser,
    LdapServiceUser,
    LdapServiceUserGroup,
    LdapUserGroup,
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


admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(LdapUserGroup, LdapUserGroupAdmin)
admin.site.register(LdapServiceUser, LdapServiceUserAdmin)
admin.site.register(LdapServiceUserGroup, LdapServiceUserGroupAdmin)
