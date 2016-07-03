# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='topologie.Room', null=True),
        ),
    ]
