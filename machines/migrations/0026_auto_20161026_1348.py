# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0025_auto_20161023_0038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(unique=True, max_length=255, help_text='Obligatoire et unique, ne doit pas comporter de points'),
        ),
    ]
