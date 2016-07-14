# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0013_auto_20160711_2240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facture',
            name='number',
        ),
        migrations.AddField(
            model_name='vente',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
