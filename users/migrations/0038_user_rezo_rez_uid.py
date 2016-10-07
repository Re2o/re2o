# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_ldapuser_login_shell'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rezo_rez_uid',
            field=models.IntegerField(null=True, blank=True, unique=True),
        ),
    ]
