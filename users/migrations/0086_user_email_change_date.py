# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-17 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0085_user_email_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_change_date',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
