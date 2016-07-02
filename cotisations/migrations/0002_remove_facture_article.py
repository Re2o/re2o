# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facture',
            name='article',
        ),
    ]
