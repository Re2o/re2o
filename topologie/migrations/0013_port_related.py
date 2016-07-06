# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0012_port_machine_interface'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='related',
            field=models.OneToOneField(null=True, to='topologie.Port', blank=True, related_name='related_port'),
        ),
    ]
