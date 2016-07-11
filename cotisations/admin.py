from django.contrib import admin

from .models import Facture, Article, Banque, Paiement, Cotisation, Vente

class FactureAdmin(admin.ModelAdmin):
    list_display = ('user','paiement','number', 'date','valid')

class VenteAdmin(admin.ModelAdmin):
    list_display = ('facture','name','prix','cotisation','duration')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name','prix','cotisation','duration')

class BanqueAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('moyen',)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('moyen',)

class CotisationAdmin(admin.ModelAdmin):
    list_display = ('facture','date_start','date_end')

admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
