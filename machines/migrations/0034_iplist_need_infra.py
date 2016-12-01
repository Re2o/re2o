# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0033_extension_need_infra'),
    ]

    operations = [
        migrations.AddField(
            model_name='iplist',
            name='need_infra',
            field=models.BooleanField(default=False),
        ),
    ]
