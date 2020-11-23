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

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [("cotisations", "0014_auto_20160712_0245")]

    operations = [
        migrations.AddField(
            model_name="facture",
            name="control",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="cotisation",
            name="facture",
            field=models.OneToOneField(to="cotisations.Facture"),
        ),
        migrations.AlterField(
            model_name="vente",
            name="facture",
            field=models.ForeignKey(to="cotisations.Facture"),
        ),
        migrations.AlterField(
            model_name="vente",
            name="number",
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
    ]
