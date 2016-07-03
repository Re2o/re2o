# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20160703_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='room',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to='topologie.Room', null=True),
        ),
    ]
