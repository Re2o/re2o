# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20160707_0105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='pwd_ssha',
        ),
    ]
