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

"""Defines the middlewares used in all apps of re2o.
"""

from django.conf import settings


def show_debug_toolbar(request):
    """Middleware to determine wether to show the toolbar.

    Compared to `django-debug-toolbar`'s default, add the possibility to allow
    any IP to see the debug panel by not setting the `INTERNAL_IPS` options

    Args:
        requests: The request object that must be checked.

    Returns:
        The boolean indicating if the debug toolbar should be shown.
    """
    if (
        hasattr(settings, "INTERNAL_IPS")
        and settings.INTERNAL_IPS
        and request.META.get("REMOTE_ADDR", None) not in settings.INTERNAL_IPS
    ):
        return False

    return bool(settings.DEBUG)
