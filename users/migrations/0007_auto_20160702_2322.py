# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_ban'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ban',
            name='date_start',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
