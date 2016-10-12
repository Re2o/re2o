# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0019_auto_20160718_1141'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machine',
            name='type',
        ),
        migrations.AddField(
            model_name='interface',
            name='type',
            field=models.ForeignKey(to='machines.MachineType', default=1, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=False,
        ),
    ]
