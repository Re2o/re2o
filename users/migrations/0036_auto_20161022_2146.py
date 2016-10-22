# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_auto_20161018_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DISABLED'), (2, 'STATE_ARCHIVE')]),
        ),
    ]
