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

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Facture, Article, Banque, Paiement, Cotisation, Vente

class FactureAdmin(VersionAdmin):
    list_display = ('user','paiement','date','valid','control')

class VenteAdmin(VersionAdmin):
    list_display = ('facture','name','prix','number','iscotisation','duration')

class ArticleAdmin(VersionAdmin):
    list_display = ('name','prix','iscotisation','duration')

class BanqueAdmin(VersionAdmin):
    list_display = ('name',)

class PaiementAdmin(VersionAdmin):
    list_display = ('moyen','type_paiement')

class CotisationAdmin(VersionAdmin):
    list_display = ('vente','date_start','date_end')

admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
