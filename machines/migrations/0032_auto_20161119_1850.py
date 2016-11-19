# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0031_auto_20161119_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='origin',
            field=models.OneToOneField(null=True, to='machines.IpList', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='extension',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
