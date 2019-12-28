# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-21 04:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0023_auto_20171015_2033")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="all_can_create",
            field=models.BooleanField(
                default=False, help_text="Tous les users peuvent en créer d'autres"
            ),
        )
    ]
