# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0009_auto_20160703_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='building',
            new_name='name',
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='room',
            name='details',
        ),
        migrations.RemoveField(
            model_name='room',
            name='number',
        ),
        migrations.RemoveField(
            model_name='room',
            name='room',
        ),
    ]
