# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-08-05 12:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0089_auto_20180805_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipv6list',
            name='ipv6',
            field=models.GenericIPAddressField(protocol='IPv6'),
        ),
    ]
