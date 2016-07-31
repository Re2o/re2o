# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_user_uid_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uid_number',
            field=models.IntegerField(default=users.models.User.auto_uid),
        ),
    ]
