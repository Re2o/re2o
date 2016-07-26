# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_ldapuser_sambasid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapuser',
            name='sambaSID',
            field=ldapdb.models.fields.IntegerField(db_column='sambaSID', unique=True),
        ),
    ]
