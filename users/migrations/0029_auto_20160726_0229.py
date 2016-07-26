# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20160726_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapuser',
            name='display_name',
            field=ldapdb.models.fields.CharField(db_column='displayName', max_length=200),
        ),
    ]
