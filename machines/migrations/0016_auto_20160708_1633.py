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
import machines.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("machines", "0015_auto_20160707_0105")]

    operations = [
        migrations.CreateModel(
            name="Extension",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name="interface",
            name="dns",
            field=models.CharField(
                unique=True,
                max_length=255,
                help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points",
            ),
        ),
        migrations.AddField(
            model_name="machinetype",
            name="extension",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="machines.Extension",
            ),
        ),
    ]
