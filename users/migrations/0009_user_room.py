# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0009_auto_20160703_1200'),
        ('users', '0008_user_registered'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='room',
            field=models.ForeignKey(to='topologie.Room', on_delete=django.db.models.deletion.PROTECT, default=1),
            preserve_default=False,
        ),
    ]
