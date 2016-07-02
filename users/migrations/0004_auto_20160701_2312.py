# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_listrights_rights'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ListRights',
            new_name='ListRight',
        ),
        migrations.RenameModel(
            old_name='Rights',
            new_name='Right',
        ),
    ]
