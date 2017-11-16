# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-16 07:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0068_auto_20171116_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extension',
            name='origin_v6',
            field=models.GenericIPAddressField(blank=True, help_text='Enregistrement AAAA associé à la zone', null=True, protocol='IPv6'),
        ),
    ]
