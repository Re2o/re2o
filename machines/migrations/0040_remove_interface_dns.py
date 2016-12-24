# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0039_auto_20161224_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='dns',
        ),
    ]
