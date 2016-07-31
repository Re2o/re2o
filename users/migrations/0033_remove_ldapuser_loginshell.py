# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_auto_20160727_2122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldapuser',
            name='loginShell',
        ),
    ]
