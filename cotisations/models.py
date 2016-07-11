from django.db import models


class Facture(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    banque = models.ForeignKey('Banque', on_delete=models.PROTECT, blank=True, null=True)
    cheque = models.CharField(max_length=255, blank=True)
    number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField(default=True)

    def prix(self):
        prix = Vente.objects.all().filter(facture=self).aggregate(models.Sum('prix'))['prix__sum']
        return prix

    def prix_total(self):
        return self.prix()*self.number

    def name(self):
        name = ' - '.join(vente.name for vente in Vente.objects.all().filter(facture=self))
        return name

    def __str__(self):
        return str(self.date) + ' ' + str(self.user)

class Vente(models.Model):
    facture = models.ForeignKey('Facture', on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    cotisation = models.BooleanField()
    duration = models.IntegerField(help_text="Durée exprimée en mois entiers", blank=True, null=True)

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)

class Article(models.Model):
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    cotisation = models.BooleanField()
    duration = models.IntegerField(help_text="Durée exprimée en mois entiers", blank=True, null=True)

    def __str__(self):
        return self.name

class Banque(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Paiement(models.Model):
    moyen = models.CharField(max_length=255)

    def __str__(self):
        return self.moyen

class Cotisation(models.Model):
    facture = models.OneToOneField('Facture', on_delete=models.PROTECT)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    def __str__(self):
        return str(self.facture)

