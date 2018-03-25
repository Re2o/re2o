# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-25 22:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0043_renamenewswitch'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Borne',
            new_name='AccessPoint',
        ),
        migrations.AlterModelOptions(
            name='accesspoint',
            options={'permissions': (('view_ap', 'Peut voir une borne'),)},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={'permissions': (('view_switch', 'Peut voir un objet switch'),)},
        ),
    ]
