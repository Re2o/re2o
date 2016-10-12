# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0011_auto_20160704_0105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(max_length=255, help_text='Obligatoire et unique', unique=True),
        ),
    ]
