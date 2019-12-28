# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-17 14:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("topologie", "0022_auto_20161211_1622")]

    operations = [
        migrations.CreateModel(
            name="Stack",
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
                ("name", models.CharField(blank=True, max_length=32, null=True)),
                ("stack_id", models.CharField(max_length=32, unique=True)),
                ("details", models.CharField(blank=True, max_length=255, null=True)),
                ("member_id_min", models.IntegerField()),
                ("member_id_max", models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name="switch",
            name="stack_member_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="switch",
            name="stack",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="topologie.Stack",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="switch", unique_together=set([("stack", "stack_member_id")])
        ),
    ]
