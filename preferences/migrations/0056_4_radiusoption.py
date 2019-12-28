# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-04 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0056_3_radiusoption")]

    operations = [
        migrations.AlterField(
            model_name="radiusoption",
            name="unknown_port",
            field=models.CharField(
                choices=[
                    ("REJECT", "Reject the machine"),
                    ("SET_VLAN", "Place the machine on the VLAN"),
                ],
                default="REJECT",
                max_length=32,
                verbose_name="Policy for unknown port",
            ),
        )
    ]
