# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-14 23:03
from __future__ import unicode_literals

from django.db import migrations, models
import preferences.aes_field


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0038_auto_20180114_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='assooption',
            name='payment_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
