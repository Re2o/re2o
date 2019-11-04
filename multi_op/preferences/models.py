# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2019  Gabriel Détraz
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
Fichier définissant les administration des models de preference 
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _


class Preferences(models.Model):
    """ Definition of the app settings"""

    enabled_dorm = models.ManyToManyField(
        "topologie.Dormitory",
        related_name="vlan_tagged",
        blank=True,
        verbose_name=_("Enabled dorm"),
    )

    class Meta:
        verbose_name = _("Dormitory of connection settings")
