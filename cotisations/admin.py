from django.contrib import admin

from .models import Facture, Article, Banque, Paiement

class FactureAdmin(admin.ModelAdmin):
    list_display = ('user','paiement','name', 'number', 'date')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name','prix')

class BanqueAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PaiementAdmin(admin.ModelAdmin):
    list_display = ('moyen',)

admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
