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

    dependencies = [("machines", "0035_auto_20161224_1201")]

    operations = [
        migrations.RenameField(model_name="domain", old_name="alias", new_name="name"),
        migrations.AlterField(
            model_name="domain",
            name="interface_parent",
            field=models.ForeignKey(to="machines.Interface", null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name="domain", unique_together=set([("name", "extension")])
        ),
    ]
