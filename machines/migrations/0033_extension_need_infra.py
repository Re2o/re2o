# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0032_auto_20161119_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='need_infra',
            field=models.BooleanField(default=False),
        ),
    ]
