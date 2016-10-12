# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0008_remove_interface_ipv6'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=False, max_length=17, unique=True),
        ),
    ]
