# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-29 02:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("topologie", "0054_auto_20180326_1742")]

    operations = [
        migrations.AlterModelOptions(
            name="accesspoint",
            options={"permissions": (("view_accesspoint", "Peut voir une borne"),)},
        )
    ]
