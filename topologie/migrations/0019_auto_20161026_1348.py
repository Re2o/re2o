# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0026_auto_20161026_1348'),
        ('topologie', '0018_room_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='location',
            field=models.CharField(default='test', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='switch',
            name='switch_interface',
            field=models.OneToOneField(default=1, to='machines.Interface'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='switch',
            name='building',
        ),
    ]
