# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0007_auto_20160703_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, default=1, to='topologie.Room'),
            preserve_default=False,
        ),
    ]
