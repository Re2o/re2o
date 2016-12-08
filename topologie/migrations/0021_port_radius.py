# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0020_auto_20161119_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='radius',
            field=models.CharField(choices=[('NO', 'NO'), ('STRICT', 'STRICT'), ('BLOQ', 'BLOQ'), ('COMMON', 'COMMON'), (7, 7), (8, 8), (42, 42), (69, 69)], max_length=32, default='NO'),
        ),
    ]
