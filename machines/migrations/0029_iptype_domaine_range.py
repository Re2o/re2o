# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0028_iptype_domaine_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='iptype',
            name='domaine_range',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(8), django.core.validators.MaxValueValidator(32)], blank=True),
        ),
    ]
