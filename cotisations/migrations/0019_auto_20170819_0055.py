# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-18 22:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cotisations", "0018_paiement_type_paiement")]

    operations = [
        migrations.AlterField(
            model_name="paiement",
            name="type_paiement",
            field=models.CharField(
                choices=[(0, "Autre"), (1, "Chèque")], default=0, max_length=255
            ),
        )
    ]
