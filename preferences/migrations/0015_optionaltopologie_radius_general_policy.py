# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-02 13:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("preferences", "0014_generaloption_email_from")]

    operations = [
        migrations.AddField(
            model_name="optionaltopologie",
            name="radius_general_policy",
            field=models.CharField(
                choices=[
                    ("MACHINE", "Sur le vlan de la plage ip machine"),
                    ("DEFINED", "Prédéfini"),
                ],
                default="DEFINED",
                max_length=32,
            ),
        )
    ]
