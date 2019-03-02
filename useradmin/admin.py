# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Alexandre Iooss
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

from django.contrib import admin

from preferences.models import GeneralOption


class UserAdmin(admin.sites.AdminSite):
    def has_permission(self, request):
        """This admin site doesn't require being staff"""
        return request.user.is_active


class ModelUserAdmin(admin.ModelAdmin):
    # Display actions on changelist bottom bu default
    actions_on_bottom = True

    # Correct number of item per page
    list_per_page = GeneralOption.get_cached_value('pagination_number')

    # Custom templates
    change_form_template = 'useradmin/change_form.html'


# Defines new management site
user_admin_site = UserAdmin(name='user_admin')
