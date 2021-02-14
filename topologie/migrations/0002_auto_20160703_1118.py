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


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("topologie", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Port",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                ("port", models.IntegerField()),
                ("details", models.CharField(max_length=255, blank=True)),
                ("_object_id", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "_content_type",
                    models.ForeignKey(
                        null=True, blank=True, to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),
                (
                    "switch",
                    models.ForeignKey(related_name="ports", to="topologie.Switch", on_delete=models.CASCADE),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="port", unique_together=set([("_content_type", "_object_id")])
        ),
    ]
