# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2021  Jean-Romain Garnier
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
Footprint optional app views
"""

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.http import JsonResponse

from users.models import User
from re2o.acl import can_view

from .utils import get_user_monthly_emissions, get_user_monthly_data_usage


@login_required
@can_view(User)
def get_data_usage_estimate(request, user, userid):
    """View used to compute a user's estimated data usage."""
    data = None
    error = None
    try:
        user_req = User.objects.get(pk=userid)
    except User.DoesNotExist:
        return JsonResponse({"data": None, "error": _("Nonexistent user.")})

    try:
        data = get_user_monthly_data_usage(request, user_req)
    except Exception:
        return JsonResponse({"data": None, "error": _("Failed to compute data usage.")})

    return JsonResponse({"data": data, "error": None})


# Canonic views for optional apps
def aff_profil(request, user):
    """View used to display the footprint on a user's profile."""

    monthly_emissions = get_user_monthly_emissions(request, user)

    context = {
        "user": user,
        "monthly_emissions": monthly_emissions,
    }
    return render_to_string(
        "footprint/aff_profil.html", context=context, request=request, using=None
    )
