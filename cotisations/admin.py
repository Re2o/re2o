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
    list_display = ('moyen',)

class CotisationAdmin(VersionAdmin):
    list_display = ('vente','date_start','date_end')

admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
