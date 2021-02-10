# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Arthur Grisel-Davy
# Copyright © 2020  Gabriel Détraz
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
Ticket preferences model
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _

from preferences.models import PreferencesModel
from re2o.mixins import AclMixin, RevMixin


class TicketOption(AclMixin, PreferencesModel):
    """Definition of the settings of tickets."""

    publish_address = models.EmailField(
        help_text=_(
            "Email address to publish the new tickets (leave empty for no publication)."
        ),
        max_length=1000,
        null=True,
    )

    class Meta:
        verbose_name = _("tickets options")
        permissions = (("view_ticketoption", _("Can view tickets options")),)
