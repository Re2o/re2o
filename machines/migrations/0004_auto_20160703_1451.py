# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0003_auto_20160703_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iplist',
            name='ipv4',
            field=models.GenericIPAddressField(protocol='IPv4', unique=True),
        ),
    ]
