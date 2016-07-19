# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0017_auto_20160718_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='details',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
