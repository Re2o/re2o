# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0038_auto_20161224_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='interface_parent',
            field=models.OneToOneField(blank=True, null=True, to='machines.Interface'),
        ),
    ]
