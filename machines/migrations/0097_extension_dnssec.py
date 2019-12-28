# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-24 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("machines", "0096_auto_20181013_1417")]

    operations = [
        migrations.AddField(
            model_name="extension",
            name="dnssec",
            field=models.BooleanField(
                default=False, help_text="Should the zone be signed with DNSSEC"
            ),
        )
    ]
