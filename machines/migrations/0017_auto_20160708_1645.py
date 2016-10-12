# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0016_auto_20160708_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machinetype',
            name='extension',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=1, to='machines.Extension'),
            preserve_default=False,
        ),
    ]
