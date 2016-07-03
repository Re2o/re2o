# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0003_room'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([('building', 'number')]),
        ),
    ]
