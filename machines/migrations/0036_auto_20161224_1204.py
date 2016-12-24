# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0035_auto_20161224_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain',
            old_name='alias',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='domain',
            name='interface_parent',
            field=models.ForeignKey(to='machines.Interface', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='domain',
            unique_together=set([('name', 'extension')]),
        ),
    ]
