# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_auto_20161119_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='listright',
            name='details',
            field=models.CharField(help_text='Description', max_length=255, blank=True),
        ),
    ]
