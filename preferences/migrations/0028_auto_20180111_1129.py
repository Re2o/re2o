# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-11 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0027_merge_20180106_2019")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="max_recharge",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=5),
        )
    ]
