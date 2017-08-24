# Re2o un logiciel d'administration développé initiallement au rezometz. Il
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


from django.db import models
from cotisations.models import Paiement

class OptionalUser(models.Model):
    PRETTY_NAME = "Options utilisateur"

    is_tel_mandatory = models.BooleanField(default=True)
    user_solde = models.BooleanField(default=False)
    solde_negatif = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    gpg_fingerprint = models.BooleanField(default=True)

    def clean(self):
        if self.user_solde:
            Paiement.objects.get_or_create(moyen="Solde")

class OptionalMachine(models.Model):
    PRETTY_NAME = "Options machines"

    password_machine = models.BooleanField(default=False)
    max_lambdauser_interfaces = models.IntegerField(default=10)
    max_lambdauser_aliases = models.IntegerField(default=10)

#class OptionalTopologie(models.Model):


class GeneralOption(models.Model):
    PRETTY_NAME = "Options générales"

    search_display_page = models.IntegerField(default=15)
    pagination_number = models.IntegerField(default=25)
    pagination_large_number = models.IntegerField(default=8)

class Service(models.Model):
    name = models.CharField(max_length=32)
    url = models.URLField()
    description = models.TextField()
    image = models.ImageField(upload_to='logo', blank=True)    

class AssoOption(models.Model):
    PRETTY_NAME = "Options de l'association"

    name = models.CharField(default="Association réseau école machin", max_length=256)
    siret = models.CharField(default="00000000000000", max_length=32)
    adresse1 = models.CharField(default="1 Rue de exemple", max_length=128)
    adresse2 = models.CharField(default="94230 Cachan", max_length=128)
    contact = models.EmailField(default="contact@example.org")
    telephone = models.CharField(max_length=15, default="0000000000")
    pseudo = models.CharField(default="Asso", max_length=32)
    utilisateur_asso = models.OneToOneField('users.User', on_delete=models.PROTECT, blank=True, null=True)
