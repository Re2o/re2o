# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0005_auto_20160703_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='room',
            name='building',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='room',
            name='number',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('building', 'room', 'number')]),
        ),
    ]
