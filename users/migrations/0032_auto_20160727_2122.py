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
import users.models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [("users", "0031_auto_20160726_0359")]

    operations = [
        migrations.CreateModel(
            name="LdapServiceUser",
            fields=[
                ("dn", models.CharField(max_length=200)),
                (
                    "name",
                    ldapdb.models.fields.CharField(
                        db_column="cn",
                        max_length=200,
                        serialize=False,
                        primary_key=True,
                    ),
                ),
                (
                    "user_password",
                    ldapdb.models.fields.CharField(
                        db_column="userPassword", blank=True, max_length=200, null=True
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ServiceUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, verbose_name="last login", null=True
                    ),
                ),
                (
                    "pseudo",
                    models.CharField(
                        max_length=32,
                        help_text="Doit contenir uniquement des lettres, chiffres, ou tirets",
                        unique=True,
                        validators=[users.models.linux_user_validator],
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
