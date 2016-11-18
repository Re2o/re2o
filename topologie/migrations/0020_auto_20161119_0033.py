# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0019_auto_20161026_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='machine_interface',
            field=models.ForeignKey(blank=True, to='machines.Interface', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
