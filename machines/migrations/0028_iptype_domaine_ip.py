# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0027_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='iptype',
            name='domaine_ip',
            field=models.GenericIPAddressField(blank=True, unique=True, null=True, protocol='IPv4'),
        ),
    ]
