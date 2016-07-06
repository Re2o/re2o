# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0014_auto_20160706_1220'),
        ('topologie', '0011_auto_20160704_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='machine_interface',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, null=True, blank=True, to='machines.Interface'),
        ),
    ]
