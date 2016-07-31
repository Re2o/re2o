# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_remove_ldapuser_loginshell'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uid_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
