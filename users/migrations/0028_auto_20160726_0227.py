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
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("users", "0027_auto_20160726_0216")]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="ldapuser",
                    name="display_name",
                    field=ldapdb.models.fields.CharField(
                        null=True, blank=True, max_length=200, db_column="displayName"
                    ),
                ),
                migrations.AddField(
                    model_name="ldapuser",
                    name="sambat_nt_password",
                    field=ldapdb.models.fields.CharField(
                        null=True,
                        blank=True,
                        max_length=200,
                        db_column="sambaNTPassword",
                    ),
                ),
                migrations.AddField(
                    model_name="ldapuser",
                    name="user_password",
                    field=ldapdb.models.fields.CharField(
                        null=True, blank=True, max_length=200, db_column="userPassword"
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    'ALTER TABLE users_ldapuser ADD COLUMN "displayName" varchar(200) NULL;'
                ),
                migrations.RunSQL(
                    'ALTER TABLE users_ldapuser ADD COLUMN "sambaNTPassword" varchar(200) NULL;'
                ),
                migrations.RunSQL(
                    'ALTER TABLE users_ldapuser ADD COLUMN "userPassword" varchar(200) NULL;'
                ),
            ],
        ),
        migrations.AddField(
            model_name="ldapuser",
            name="macs",
            field=ldapdb.models.fields.ListField(
                null=True,
                blank=True,
                max_length=200,
                db_column="radiusCallingStationId",
            ),
        ),
        migrations.AddField(
            model_name="listright",
            name="gid",
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="shell",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                default=1,
                to="users.ListShell",
            ),
        ),
    ]
