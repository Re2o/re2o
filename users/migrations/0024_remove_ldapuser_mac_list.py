# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20160724_1908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldapuser',
            name='mac_list',
        ),
    ]
