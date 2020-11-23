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
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [("users", "0020_request")]

    operations = [
        migrations.CreateModel(
            name="LdapUser",
            fields=[
                ("dn", models.CharField(max_length=200)),
                ("gid", ldapdb.models.fields.IntegerField(db_column="gidNumber")),
                (
                    "name",
                    ldapdb.models.fields.CharField(
                        primary_key=True,
                        max_length=200,
                        db_column="cn",
                        serialize=False,
                    ),
                ),
                (
                    "uid",
                    ldapdb.models.fields.CharField(max_length=200, db_column="uid"),
                ),
                (
                    "uidNumber",
                    ldapdb.models.fields.IntegerField(
                        unique=True, db_column="uidNumber"
                    ),
                ),
                ("sn", ldapdb.models.fields.CharField(max_length=200, db_column="sn")),
                (
                    "loginShell",
                    ldapdb.models.fields.CharField(
                        default="/bin/zsh", max_length=200, db_column="loginShell"
                    ),
                ),
                (
                    "mail",
                    ldapdb.models.fields.CharField(max_length=200, db_column="mail"),
                ),
                (
                    "given_name",
                    ldapdb.models.fields.CharField(
                        max_length=200, db_column="givenName"
                    ),
                ),
                (
                    "home_directory",
                    ldapdb.models.fields.CharField(
                        max_length=200, db_column="homeDirectory"
                    ),
                ),
                (
                    "dialupAccess",
                    ldapdb.models.fields.CharField(
                        max_length=200, db_column="dialupAccess"
                    ),
                ),
                (
                    "mac_list",
                    ldapdb.models.fields.CharField(
                        max_length=200, db_column="radiusCallingStationId"
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
