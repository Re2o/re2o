# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-02 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0025_merge_20170902_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='radius',
            field=models.CharField(choices=[('NO', 'NO'), ('STRICT', 'STRICT'), ('BLOQ', 'BLOQ'), ('COMMON', 'COMMON'), ('3', '3'), ('7', '7'), ('8', '8'), ('13', '13'), ('20', '20'), ('42', '42'), ('69', '69')], default='NO', max_length=32),
        ),
    ]
