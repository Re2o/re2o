# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-16 22:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0084_auto_20191120_0159'),
    ]

    def flag_verified(apps, schema_editor):
        db_alias = schema_editor.connection.alias
        users = apps.get_model("users", "User")
        users.objects.using(db_alias).all().update(email_state=0)

    def undo_flag_verified(apps, schema_editor):
        return

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_state',
            field=models.IntegerField(choices=[(0, 'Verified'), (1, 'Unverified'), (2, 'Waiting for email confirmation')], default=2),
        ),
        migrations.RunPython(flag_verified, undo_flag_verified),
    ]
