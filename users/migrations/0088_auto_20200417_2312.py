# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-17 21:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0087_request_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_change_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2020, 4, 17, 21, 12, 19, 739799, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
