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
Deposits utils
"""
from re2o.base import SortTable


class DepositSortTable(SortTable):
    """Extension of the SortTable class to handle the deposit optional app"""

    DEPOSIT_INDEX = {
        "deposit_user": ["user__pseudo"],
        "deposit_item": ["item__name"],
        "deposit_payment": ["payment_method__moyen"],
        "deposit_date": ["date"],
        "deposit_returned": ["returned"],
        "deposit_amount": ["deposit_amount"],
        "default": ["-date"],
    }
