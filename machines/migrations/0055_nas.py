# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-10 21:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("machines", "0054_text_zone")]

    operations = [
        migrations.CreateModel(
            name="Nas",
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "machine_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="machinetype_on_nas",
                        to="machines.MachineType",
                    ),
                ),
                (
                    "nas_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="nas_type",
                        to="machines.MachineType",
                    ),
                ),
            ],
        )
    ]
