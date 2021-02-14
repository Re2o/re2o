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
"""cotisations.admin
The objects, fields and datastructures visible in the Django admin view
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (Article, Banque, CostEstimate, Cotisation, CustomInvoice,
                     Facture, Paiement, Vente)


class FactureAdmin(VersionAdmin):
    """Admin class for invoices."""

    pass


class CostEstimateAdmin(VersionAdmin):
    """Admin class for cost estimates."""

    pass


class CustomInvoiceAdmin(VersionAdmin):
    """Admin class for custom invoices."""

    pass


class VenteAdmin(VersionAdmin):
    """Admin class for purchases."""

    pass


class ArticleAdmin(VersionAdmin):
    """Admin class for articles."""

    pass


class BanqueAdmin(VersionAdmin):
    """Admin class for banks."""

    pass


class PaiementAdmin(VersionAdmin):
    """Admin class for payment methods."""

    pass


class CotisationAdmin(VersionAdmin):
    """Admin class for subscriptions."""

    pass


admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
admin.site.register(CustomInvoice, CustomInvoiceAdmin)
admin.site.register(CostEstimate, CostEstimateAdmin)
