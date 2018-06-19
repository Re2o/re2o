# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-16 03:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0058_remove_switch_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='switch',
            name='model',
            field=models.ForeignKey(blank=True, help_text='Modèle du switch', null=True, on_delete=django.db.models.deletion.SET_NULL, to='topologie.ModelSwitch'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='number',
            field=models.PositiveIntegerField(help_text='Nombre de ports'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='stack_member_id',
            field=models.PositiveIntegerField(blank=True, help_text='Baie de brassage du switch', null=True),
        ),
        migrations.AlterField(
            model_name='switch',
            name='switchbay',
            field=models.ForeignKey(blank=True, help_text='Baie de brassage du switch', null=True, on_delete=django.db.models.deletion.SET_NULL, to='topologie.SwitchBay'),
        ),
    ]