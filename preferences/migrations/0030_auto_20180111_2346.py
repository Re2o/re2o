# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-11 22:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0029_auto_20180111_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='optionaluser',
            name='max_recharge',
        ),
        migrations.AddField(
            model_name='optionaluser',
            name='max_solde',
            field=models.DecimalField(decimal_places=2, default=50, max_digits=5),
        ),
    ]
