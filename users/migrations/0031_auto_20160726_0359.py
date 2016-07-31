# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_auto_20160726_0357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shell',
            field=models.ForeignKey(to='users.ListShell', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True),
        ),
    ]
