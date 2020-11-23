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


class Migration(migrations.Migration):

    dependencies = [("users", "0015_whitelist")]

    operations = [
        migrations.AlterField(
            model_name="ban",
            name="date_end",
            field=models.DateTimeField(help_text="%d/%m/%y %H:%M:%S"),
        ),
        migrations.AlterField(
            model_name="user",
            name="pseudo",
            field=models.CharField(
                unique=True,
                validators=[users.models.linux_user_validator],
                max_length=32,
                help_text="Doit contenir uniquement des lettres, chiffres, ou tirets",
            ),
        ),
        migrations.AlterField(
            model_name="whitelist",
            name="date_end",
            field=models.DateTimeField(help_text="%d/%m/%y %H:%M:%S"),
        ),
    ]
