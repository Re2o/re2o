# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20160707_0115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listright',
            name='listright',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
