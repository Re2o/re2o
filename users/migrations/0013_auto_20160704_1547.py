# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20160703_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='comment',
            field=models.CharField(max_length=255, help_text="Infos sur l'etablissement (optionnel)", blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='promo',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
