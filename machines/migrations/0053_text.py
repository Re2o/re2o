# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-05 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("machines", "0052_auto_20170828_2322")]

    operations = [
        migrations.CreateModel(
            name="Text",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("field1", models.CharField(max_length=255)),
                ("field2", models.CharField(max_length=255)),
            ],
        )
    ]
