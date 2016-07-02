# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0009_remove_cotisation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='duration',
            field=models.IntegerField(null=True, help_text='Durée exprimée en mois entiers', blank=True),
        ),
    ]
