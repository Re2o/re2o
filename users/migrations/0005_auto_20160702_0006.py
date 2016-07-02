# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20160701_2312'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='right',
            unique_together=set([('user', 'right')]),
        ),
    ]
