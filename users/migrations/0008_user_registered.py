# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20160702_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='registered',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 7, 2, 23, 25, 21, 698883, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
