# ⁻*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Gabriel Detraz
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

from django.core.management.base import BaseCommand, CommandError
from pymongo import MongoClient
from topologie.models import Borne

class Command(BaseCommand):
    help = 'Ce script donne un nom aux bornes dans le controleur unifi.
    A lancer sur le serveur en local où se trouve le controleur'

    def handle(self, *args, **options):
        # Connexion mongodb
        client = MongoClient("mongodb://localhost:27117")
        db = client.ace
        device = db['device']

        bornes = Borne.objects.all()
        
        def set_bornes_names(liste_bornes):
            """Met à jour les noms des bornes dans la bdd du controleur"""
            for borne in liste_bornes:
                if borne.ipv4 and borne.domain:
                    device.find_one_and_update({'ip': str(borne.ipv4)}, {'$set': {'name': str(borne.domain.name)}})
            return

        set_bornes_names(bornes)

        self.stdout.write(self.style.SUCCESS('Mise à jour de la base de donnée unifi avec succès'))
