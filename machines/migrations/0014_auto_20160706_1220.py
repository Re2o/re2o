# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import machines.models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0013_auto_20160705_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(unique=True,  max_length=255, help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points"),
        ),
    ]
