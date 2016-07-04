# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0009_auto_20160703_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='name',
            field=models.CharField(blank=True, unique=True, max_length=255, help_text='Optionnel', null=True),
        ),
    ]
