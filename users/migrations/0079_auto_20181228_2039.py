# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-28 19:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0078_auto_20181011_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=49, null=True),
        ),
    ]
