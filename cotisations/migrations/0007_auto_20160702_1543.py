# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0006_auto_20160702_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='name',
            field=models.CharField(default='plop', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='facture',
            name='prix',
            field=models.DecimalField(default=1, max_digits=5, decimal_places=2),
            preserve_default=False,
        ),
    ]
