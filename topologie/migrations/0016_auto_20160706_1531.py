# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0015_auto_20160706_1452'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='port',
            name='related',
        ),
        migrations.AddField(
            model_name='port',
            name='related',
            field=models.OneToOneField(blank=True, to='topologie.Port', related_name='related_port', null=True),
        ),
    ]
