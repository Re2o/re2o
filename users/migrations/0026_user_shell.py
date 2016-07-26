# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_listshell'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shell',
            field=models.ForeignKey(to='users.ListShell', default=1, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=False,
        ),
    ]
