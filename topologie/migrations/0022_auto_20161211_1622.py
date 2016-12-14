# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0021_port_radius'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='radius',
            field=models.CharField(max_length=32, default='NO', choices=[('NO', 'NO'), ('STRICT', 'STRICT'), ('BLOQ', 'BLOQ'), ('COMMON', 'COMMON'), ('7', '7'), ('8', '8'), ('42', '42'), ('69', '69')]),
        ),
    ]
