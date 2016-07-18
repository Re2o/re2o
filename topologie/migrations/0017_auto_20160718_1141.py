# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0016_auto_20160706_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='machine_interface',
            field=models.OneToOneField(to='machines.Interface', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
    ]
