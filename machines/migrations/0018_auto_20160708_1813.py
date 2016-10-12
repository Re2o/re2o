# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0017_auto_20160708_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points", unique=True, max_length=255),
        ),
    ]
