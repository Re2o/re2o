# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018 Maël Kervella
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

"""Defines the ACL for the whole API.

Importing this module, creates the 'can view api' permission if not already
done.
"""

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


def _create_api_permission():
    """Creates the 'use_api' permission if not created.

    The 'use_api' is a fake permission in the sense it is not associated with an
    existing model and this ensure the permission is created every time this file
    is imported.
    """
    api_content_type, created = ContentType.objects.get_or_create(
        app_label=settings.API_CONTENT_TYPE_APP_LABEL,
        model=settings.API_CONTENT_TYPE_MODEL,
    )
    if created:
        api_content_type.save()
    api_permission, created = Permission.objects.get_or_create(
        name=settings.API_PERMISSION_NAME,
        content_type=api_content_type,
        codename=settings.API_PERMISSION_CODENAME,
    )
    if created:
        api_permission.save()


#_create_api_permission()


def can_view(user, *args, **kwargs):
    """Check if an user can view the application.

    Args:
        user: The user who wants to view the application.

    Returns:
        A couple (allowed, msg) where allowed is a boolean which is True if
        viewing is granted and msg is a message (can be None).
    """
    kwargs = {
        "app_label": settings.API_CONTENT_TYPE_APP_LABEL,
        "codename": settings.API_PERMISSION_CODENAME,
    }
    permission = "%(app_label)s.%(codename)s" % kwargs
    can = user.has_perm(permission)
    return (
        can,
        None if can else _("You don't have the right to view this application."),
        (permission,),
    )
