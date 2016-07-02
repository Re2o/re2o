# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0010_auto_20160702_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotisation',
            name='date_start',
            field=models.DateTimeField(),
        ),
    ]
