# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-12 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0030_auto_20180111_2346")]

    operations = [
        migrations.AddField(
            model_name="optionaluser",
            name="self_adhesion",
            field=models.BooleanField(
                default=False,
                help_text="Un nouvel utilisateur peut se créer son compte sur re2o",
            ),
        )
    ]
