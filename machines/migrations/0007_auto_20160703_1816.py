# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0006_auto_20160703_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='ipv6',
            field=models.GenericIPAddressField(null=True, protocol='IPv6'),
        ),
    ]
