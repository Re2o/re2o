# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_auto_20160726_0229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapuser',
            name='display_name',
            field=ldapdb.models.fields.CharField(null=True, max_length=200, db_column='displayName', blank=True),
        ),
    ]
