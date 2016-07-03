# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0002_auto_20160703_0103'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('details', models.CharField(blank=True, max_length=255)),
                ('port', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='topologie.Port')),
                ('room', models.ForeignKey(to='topologie.Room', on_delete=django.db.models.deletion.PROTECT, blank=True)),
            ],
        ),
    ]
