# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-24 19:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0007_auto_20170824_2056'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assooption',
            name='adresse',
        ),
        migrations.AddField(
            model_name='assooption',
            name='adresse1',
            field=models.CharField(default='1 Rue de exemple', max_length=128),
        ),
        migrations.AddField(
            model_name='assooption',
            name='adresse2',
            field=models.CharField(default='94230 Cachan', max_length=128),
        ),
        migrations.AlterField(
            model_name='assooption',
            name='name',
            field=models.CharField(default='Association réseau école machin', max_length=256),
        ),
    ]
