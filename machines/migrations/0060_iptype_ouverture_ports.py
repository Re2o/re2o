# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-03 16:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("machines", "0059_iptype_prefix_v6")]

    operations = [
        migrations.AddField(
            model_name="iptype",
            name="ouverture_ports",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="machines.OuverturePortList",
            ),
        )
    ]
