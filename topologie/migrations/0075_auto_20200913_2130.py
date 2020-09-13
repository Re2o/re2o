# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-13 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0074_auto_20200419_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='dormitory',
            name='city',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dormitory',
            name='country',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dormitory',
            name='street',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dormitory',
            name='zipcode',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
