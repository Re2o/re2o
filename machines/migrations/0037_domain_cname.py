# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0036_auto_20161224_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='cname',
            field=models.OneToOneField(related_name='related_domain', null=True, to='machines.Domain', blank=True),
        ),
    ]
