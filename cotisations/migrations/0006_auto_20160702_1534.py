# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0005_auto_20160702_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='name',
            field=models.CharField(null=True, default='plop', max_length=255),
        ),
        migrations.AlterField(
            model_name='facture',
            name='prix',
            field=models.DecimalField(null=True, decimal_places=2, default=1, max_digits=5),
        ),
    ]
