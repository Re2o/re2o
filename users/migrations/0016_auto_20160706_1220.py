# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_whitelist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ban',
            name='date_end',
            field=models.DateTimeField(help_text='%d/%m/%y %H:%M:%S'),
        ),
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(unique=True, validators=[users.models.linux_user_validator], max_length=32, help_text='Doit contenir uniquement des lettres, chiffres, ou tirets'),
        ),
        migrations.AlterField(
            model_name='whitelist',
            name='date_end',
            field=models.DateTimeField(help_text='%d/%m/%y %H:%M:%S'),
        ),
    ]
