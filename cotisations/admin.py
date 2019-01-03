# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
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

from .models import Facture, Article, Banque, Paiement, Cotisation, Vente
from .models import CustomInvoice, CostEstimate
from .tex import DocumentTemplate


class FactureAdmin(VersionAdmin):
    """Class admin d'une facture, tous les champs"""
    pass


class CostEstimateAdmin(VersionAdmin):
    """Admin class for cost estimates."""
    pass


class CustomInvoiceAdmin(VersionAdmin):
    """Admin class for custom invoices."""
    pass


class VenteAdmin(VersionAdmin):
    """Class admin d'une vente, tous les champs (facture related)"""
    pass


class ArticleAdmin(VersionAdmin):
    """Class admin d'un article en vente"""
    pass


class BanqueAdmin(VersionAdmin):
    """Class admin de la liste des banques (facture related)"""
    pass


class PaiementAdmin(VersionAdmin):
    """Class admin d'un moyen de paiement (facture related"""
    pass


class CotisationAdmin(VersionAdmin):
    """Class admin d'une cotisation (date de debut et de fin),
    Vente related"""
    pass


class DocumentTemplateAdmin(VersionAdmin):
    """Admin class for DocumentTemplate"""
    pass


admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
admin.site.register(CustomInvoice, CustomInvoiceAdmin)
admin.site.register(CostEstimate, CostEstimateAdmin)
admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
