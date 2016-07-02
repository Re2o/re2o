# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0002_remove_facture_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='banque',
            field=models.ForeignKey(blank=True, to='cotisations.Banque', on_delete=django.db.models.deletion.PROTECT, null=True),
        ),
    ]
