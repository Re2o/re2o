# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-29 14:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("cotisations", "0035_notepayment")]

    operations = [
        migrations.AddField(
            model_name="custominvoice",
            name="remark",
            field=models.TextField(blank=True, null=True, verbose_name="Remark"),
        )
    ]
