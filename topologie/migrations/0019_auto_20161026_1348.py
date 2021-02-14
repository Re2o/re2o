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
        ("machines", "0026_auto_20161026_1348"),
        ("topologie", "0018_room_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="switch",
            name="location",
            field=models.CharField(default="test", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="switch",
            name="switch_interface",
            field=models.OneToOneField(default=1, to="machines.Interface", on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(name="switch", unique_together=set([])),
        migrations.RemoveField(model_name="switch", name="building"),
    ]
