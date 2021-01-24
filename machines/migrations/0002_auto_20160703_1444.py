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
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [("machines", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Interface",
            fields=[
                (
                    "id",
                    models.AutoField(
                        serialize=False,
                        verbose_name="ID",
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("ipv6", models.GenericIPAddressField(protocol="IPv6")),
                ("mac_address", macaddress.fields.MACAddressField(integer=True)),
                ("details", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255, blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="IpList",
            fields=[
                (
                    "id",
                    models.AutoField(
                        serialize=False,
                        verbose_name="ID",
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("ipv4", models.GenericIPAddressField(protocol="IPv4")),
            ],
        ),
        migrations.AddField(
            model_name="interface",
            name="ipv4",
            field=models.OneToOneField(
                null=True,
                to="machines.IpList",
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
            ),
        ),
        migrations.AddField(
            model_name="interface",
            name="machine",
            field=models.ForeignKey(
                to="machines.Machine", on_delete=django.db.models.deletion.PROTECT
            ),
        ),
    ]
