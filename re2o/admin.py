from django.contrib.admin.sites import AdminSite


class UserAdmin(AdminSite):
    def has_permission(self, request):
        """This admin site doesn't require being staff"""
        return request.user.is_active


user_admin_site = UserAdmin(name='user_admin')
