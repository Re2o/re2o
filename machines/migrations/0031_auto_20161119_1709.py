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
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [("machines", "0030_auto_20161118_1730")]

    operations = [
        migrations.CreateModel(
            name="Mx",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                ("priority", models.IntegerField(unique=True)),
                (
                    "name",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to="machines.Alias"
                    ),
                ),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="machines.Extension",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ns",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                    ),
                ),
                (
                    "interface",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="machines.Interface",
                    ),
                ),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="machines.Extension",
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="iptype",
            name="domaine_ip",
            field=models.GenericIPAddressField(protocol="IPv4"),
        ),
        migrations.AlterField(
            model_name="iptype",
            name="domaine_range",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(8),
                    django.core.validators.MaxValueValidator(32),
                ]
            ),
        ),
    ]
