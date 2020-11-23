# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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

"""cotisations.acl

Here are defined some functions to check acl on the application.
"""
from django.utils.translation import ugettext as _


def can_view(user, *args, **kwargs):
    """Check if an user can view the application.

    Args:
        user: The user who wants to view the application.

    Returns:
        A couple (allowed, msg) where allowed is a boolean which is True if
        viewing is granted and msg is a message (can be None).
    """
    can = user.has_module_perms("cotisations")
    if can:
        return can, None, ("cotisations",)
    else:
        return (
            can,
            _("You don't have the right to view this application."),
            ("cotisations",),
        )
