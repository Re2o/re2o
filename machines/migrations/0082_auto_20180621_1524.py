# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-21 20:24
from __future__ import unicode_literals

from django.db import migrations
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0081_auto_20180521_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=False, max_length=17),
        ),
    ]