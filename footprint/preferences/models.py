# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
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
footprint optional app preferences model
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from preferences.models import PreferencesModel
from re2o.mixins import AclMixin, RevMixin


class FootprintOption(AclMixin, PreferencesModel):
    """Definition of the settings of the footprint app."""

    # https://www.ademe.fr/expertises/consommer-autrement/passer-a-laction/reconnaitre-produit-plus-respectueux-lenvironnement/dossier/laffichage-environnemental/affichage-environnemental-secteur-numerique
    monthly_infra_emissions = models.DecimalField(
        verbose_name=_("Estimated monthly infrastructure emissions"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0)],
    )
    data_usage_script_path = models.CharField(
        verbose_name=_("User monthly data usage estimation script"),
        default="footprint/scripts/default_data_usage_estimator.py",
        max_length=4096,
    )
    data_usage_script_timeout = models.DecimalField(
        verbose_name=_("Estimation script timeout (in seconds)"),
        max_digits=4,
        decimal_places=2,
        default=10,
    )

    class Meta:
        verbose_name = _("Footprint preferences")
