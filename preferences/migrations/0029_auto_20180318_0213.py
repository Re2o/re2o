# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-18 01:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0028_assooption_description")]

    operations = [
        migrations.AlterField(
            model_name="assooption",
            name="description",
            field=models.TextField(blank=True, null=True),
        )
    ]
