# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0018_auto_20160708_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='machine',
            field=models.ForeignKey(to='machines.Machine'),
        ),
    ]
