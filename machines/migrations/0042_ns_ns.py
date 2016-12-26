# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0041_remove_ns_interface'),
    ]

    operations = [
        migrations.AddField(
            model_name='ns',
            name='ns',
            field=models.OneToOneField(to='machines.Domain', default=1, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=False,
        ),
    ]
