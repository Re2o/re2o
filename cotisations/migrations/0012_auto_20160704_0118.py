# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0011_auto_20160702_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotisation',
            name='facture',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='cotisations.Facture'),
        ),
    ]
