# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-10 22:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0047_auto_20180711_0015'),
        ('topologie', '0069_switch_automatic_provision'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='radius_key',
            field=models.ForeignKey(blank=True, help_text='Clef radius du switch', null=True, on_delete=django.db.models.deletion.PROTECT, to='preferences.RadiusKey'),
        ),
    ]
