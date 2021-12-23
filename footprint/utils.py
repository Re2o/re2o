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
Footprint optional app utils
"""
import os
import pathlib
import subprocess

from django.contrib import messages
from django.utils.translation import ugettext as _

from re2o.utils import all_has_access

from .preferences.models import FootprintOption


def get_user_monthly_emissions(request, user):
    if not user.has_access:
        return None

    monthly_infra_emissions = FootprintOption.get_cached_value(
        "monthly_infra_emissions"
    )
    if monthly_infra_emissions is None:
        return None

    user_count = all_has_access(including_asso=False).count()
    return monthly_infra_emissions / max(user_count, 1)


def get_user_monthly_data_usage(request, user):
    if not user.has_access:
        return None

    data_usage_script_path = FootprintOption.get_cached_value("data_usage_script_path")
    if data_usage_script_path is None:
        return None

    script_path = pathlib.Path(data_usage_script_path)
    if not script_path.is_absolute():
        re2o_base_path = pathlib.Path(__file__).parent.parent.resolve()
        script_path = re2o_base_path / script_path

    timeout = float(FootprintOption.get_cached_value("data_usage_script_timeout"))

    cmd = [script_path, str(user.id)]
    out = subprocess.check_output(cmd, timeout=timeout).decode("utf-8").strip()

    if out == "None":
        out = None
    else:
        out = float(out)

    return out
