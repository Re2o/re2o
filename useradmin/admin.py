from django.contrib import admin


class UserAdmin(admin.sites.AdminSite):
    def has_permission(self, request):
        """This admin site doesn't require being staff"""
        return request.user.is_active


class ModelUserAdmin(admin.ModelAdmin):
    # Display actions on changelist bottom bu default
    actions_on_bottom = True


# Defines new management site
user_admin_site = UserAdmin(name='user_admin')
