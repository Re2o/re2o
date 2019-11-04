# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-09 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0060_auto_20190712_1821")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="allow_archived_connexion",
            field=models.BooleanField(
                default=False,
                help_text="If True, archived users are allowed to connect.",
            ),
        )
    ]
