# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_auto_20160731_0448'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapuser',
            name='login_shell',
            field=ldapdb.models.fields.CharField(null=True, db_column='loginShell', blank=True, max_length=200),
        ),
    ]
