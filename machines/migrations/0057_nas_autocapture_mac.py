# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-14 13:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("machines", "0056_nas_port_access_mode")]

    operations = [
        migrations.AddField(
            model_name="nas",
            name="autocapture_mac",
            field=models.BooleanField(default=False),
        )
    ]
