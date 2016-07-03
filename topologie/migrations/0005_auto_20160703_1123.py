# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0004_auto_20160703_1122'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('building', 'number')]),
        ),
    ]
