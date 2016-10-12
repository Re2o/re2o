# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0012_auto_20160704_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(max_length=255, unique=True, help_text='Obligatoire et unique, doit se terminer en .rez et ne pas comporter de points'),
        ),
    ]
