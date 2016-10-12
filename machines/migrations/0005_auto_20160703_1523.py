# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0004_auto_20160703_1451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interface',
            old_name='name',
            new_name='dns',
        ),
        migrations.AddField(
            model_name='machine',
            name='name',
            field=models.CharField(blank=True, unique=True, max_length=255, help_text='Optionnel'),
        ),
    ]
