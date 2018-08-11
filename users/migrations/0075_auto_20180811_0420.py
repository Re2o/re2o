# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-08-11 02:20
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0074_auto_20180810_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=40, null=True, validators=[django.core.validators.RegexValidator('^[0-9A-F]{40}$', message='Une fingerprint GPG doit contenir 40 caractères hexadécimaux')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
