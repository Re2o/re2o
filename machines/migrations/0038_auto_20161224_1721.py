# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0037_domain_cname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='cname',
            field=models.ForeignKey(null=True, to='machines.Domain', related_name='related_domain', blank=True),
        ),
    ]
