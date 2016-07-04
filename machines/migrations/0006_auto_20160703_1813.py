# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0005_auto_20160703_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='details',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
