# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-01 22:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0091_auto_20200423_1256'),
    ]

    operations = [
        migrations.RenameField("user", "rezo_rez_uid", "legacy_uid"),
        migrations.AlterField(
            model_name='user',
            name='legacy_uid',
            field=models.PositiveIntegerField(blank=True, help_text='Optionnal legacy uid, for import and transition purpose', null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, help_text='Education institute.', null=True, on_delete=django.db.models.deletion.PROTECT, to='users.School'),
        ),
        migrations.AlterField(
            model_name='user',
            name='shell',
            field=models.ForeignKey(blank=True, help_text='Unix shell.', null=True, on_delete=django.db.models.deletion.PROTECT, to='users.ListShell'),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(choices=[(0, 'Active'), (1, 'Disabled'), (2, 'Archived'), (3, 'Not yet active'), (4, 'Fully archived')], default=3, help_text='Account state.'),
        ),
    ]
