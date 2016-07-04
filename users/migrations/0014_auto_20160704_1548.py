# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20160704_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='promo',
        ),
        migrations.AlterField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, help_text='Commentaire, promo', max_length=255),
        ),
    ]
