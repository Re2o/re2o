# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DEACTIVATED'), (2, 'STATE_ARCHIVED')]),
        ),
    ]
