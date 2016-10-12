# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0002_auto_20160703_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=True, unique=True),
        ),
    ]
