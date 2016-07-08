# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import machines.models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0014_auto_20160706_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(unique=True, validators=[machines.models.full_domain_validator], help_text="Obligatoire et unique, doit se terminer en .example et ne pas comporter d'autres points", max_length=255),
        ),
    ]
