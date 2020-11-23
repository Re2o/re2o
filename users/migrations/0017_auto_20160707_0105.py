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

from django.db import models, migrations


def move_passwords(apps, schema_editor):
    User = apps.get_model("users", "User")
    for row in User.objects.all():
        row.password = row.pwd_ssha
        row.save()


class Migration(migrations.Migration):

    dependencies = [("users", "0016_auto_20160706_1220")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_login",
            field=models.DateTimeField(
                null=True, blank=True, verbose_name="last login"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="password",
            field=models.CharField(
                verbose_name="password", default="!", max_length=128
            ),
            preserve_default=False,
        ),
        migrations.RunPython(move_passwords, reverse_code=migrations.RunPython.noop),
    ]
