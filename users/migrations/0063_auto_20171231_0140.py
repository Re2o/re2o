# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-31 00:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0062_auto_20171231_0056'),
    ]

    def transfer_right(apps, schema_editor):
        rights = apps.get_model("users", "Right")
        db_alias = schema_editor.connection.alias
        for rg in rights.objects.using(db_alias).all():
            group = rg.right
            u=rg.user
            u.groups.add(group.group_ptr)
            u.save()

    def untransfer_right(apps, schema_editor):
        return

    operations = [
    migrations.RunPython(transfer_right, untransfer_right),
    ]