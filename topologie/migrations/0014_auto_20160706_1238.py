# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0013_port_related'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('switch', 'port')]),
        ),
        migrations.RemoveField(
            model_name='port',
            name='_content_type',
        ),
        migrations.RemoveField(
            model_name='port',
            name='_object_id',
        ),
    ]
