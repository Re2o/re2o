# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0002_auto_20160703_1118'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('details', models.CharField(max_length=255, blank=True)),
                ('building', models.CharField(max_length=255, unique=True)),
                ('number', models.IntegerField()),
            ],
        ),
    ]
