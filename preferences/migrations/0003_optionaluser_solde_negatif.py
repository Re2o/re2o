# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-26 01:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0002_auto_20170625_1923")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="solde_negatif",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        )
    ]
