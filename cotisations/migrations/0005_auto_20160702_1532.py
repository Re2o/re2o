# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0004_auto_20160702_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='cheque',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
