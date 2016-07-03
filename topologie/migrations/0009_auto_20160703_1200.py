# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0008_port_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='room',
            field=models.ForeignKey(to='topologie.Room', on_delete=django.db.models.deletion.PROTECT, blank=True, null=True),
        ),
    ]
