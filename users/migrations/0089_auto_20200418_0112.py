# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-04-17 23:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0088_auto_20200417_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_state',
            field=models.IntegerField(choices=[(0, 'Confirmed'), (1, 'Not confirmed'), (2, 'Waiting for email confirmation')], default=2),
        ),
    ]