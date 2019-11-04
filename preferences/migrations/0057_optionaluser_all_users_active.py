# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-05 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0056_4_radiusoption")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="all_users_active",
            field=models.BooleanField(
                default=False,
                help_text="If True, all new created and connected users are active.                    If False, only when a valid registration has been paid",
            ),
        )
    ]
