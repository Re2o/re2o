# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0014_auto_20160712_0245'),
    ]

    operations = [
        migrations.AddField(
            model_name='facture',
            name='control',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='facture',
            field=models.OneToOneField(to='cotisations.Facture'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(to='cotisations.Facture'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='number',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
