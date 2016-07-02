# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0003_auto_20160702_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='name',
            field=models.CharField(null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='facture',
            name='prix',
            field=models.DecimalField(max_digits=5, null=True, decimal_places=2),
        ),
    ]
