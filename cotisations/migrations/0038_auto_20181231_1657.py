# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-31 22:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("cotisations", "0037_costestimate")]

    operations = [
        migrations.AlterField(
            model_name="costestimate",
            name="final_invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="origin_cost_estimate",
                to="cotisations.CustomInvoice",
            ),
        ),
        migrations.AlterField(
            model_name="costestimate",
            name="validity",
            field=models.DurationField(
                help_text="DD HH:MM:SS", verbose_name="Period of validity"
            ),
        ),
        migrations.AlterField(
            model_name="custominvoice",
            name="paid",
            field=models.BooleanField(default=False, verbose_name="Paid"),
        ),
    ]
