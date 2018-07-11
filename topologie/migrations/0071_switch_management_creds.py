# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-10 23:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0048_switchmanagementcred'),
        ('topologie', '0070_switch_radius_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='management_creds',
            field=models.ForeignKey(blank=True, help_text='Identifiant de management de ce switch', null=True, on_delete=django.db.models.deletion.PROTECT, to='preferences.SwitchManagementCred'),
        ),
    ]
