# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0022_auto_20161011_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='iplist',
            name='ip_type',
            field=models.ForeignKey(to='machines.MachineType', on_delete=django.db.models.deletion.PROTECT, default=1),
            preserve_default=False,
        ),
    ]
