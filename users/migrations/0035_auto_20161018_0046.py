# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_auto_20161018_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uid_number',
            field=models.IntegerField(unique=True, default=users.models.User.auto_uid),
        ),
    ]
