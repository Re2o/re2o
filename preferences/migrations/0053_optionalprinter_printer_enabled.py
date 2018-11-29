# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-10-20 11:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0052_optionalprinter'),
    ]

    operations = [
        migrations.AddField(
            model_name='optionalprinter',
            name='Printer_enabled',
            field=models.BooleanField(default=False, help_text='Is printer Available ?'),
        ),
    ]