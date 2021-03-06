# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-25 23:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("topologie", "0044_auto_20180326_0002")]

    operations = [
        migrations.AlterField(
            model_name="port",
            name="switch",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ports",
                to="topologie.Switch",
            ),
        )
    ]
