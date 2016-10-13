# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0023_iplist_ip_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='machinetype',
            name='need_infra',
            field=models.BooleanField(default=False),
        ),
    ]
