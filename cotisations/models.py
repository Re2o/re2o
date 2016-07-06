from django.db import models


class Facture(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    banque = models.ForeignKey('Banque', on_delete=models.PROTECT, blank=True, null=True)
    cheque = models.CharField(max_length=255, blank=True)
    number = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=5, decimal_places=2)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name) + ' ' + str(self.date) + ' ' + str(self.user)

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

