# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-29 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0026_auto_20171028_0126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
