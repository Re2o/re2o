# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0020_auto_20160718_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
