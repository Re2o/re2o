# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0014_auto_20160706_1238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='port',
            name='related',
        ),
        migrations.AddField(
            model_name='port',
            name='related',
            field=models.ManyToManyField(related_name='_port_related_+', to='topologie.Port', blank=True),
        ),
    ]
