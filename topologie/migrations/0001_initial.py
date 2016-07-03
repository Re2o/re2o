# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('building', models.CharField(max_length=10)),
                ('switch', models.IntegerField()),
                ('port', models.IntegerField()),
                ('details', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('details', models.CharField(blank=True, max_length=255)),
                ('room', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('building', 'switch', 'port')]),
        ),
    ]
