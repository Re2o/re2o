# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0026_auto_20161026_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('alias', models.CharField(max_length=255, help_text='Obligatoire et unique, ne doit pas comporter de points', unique=True)),
                ('interface_parent', models.ForeignKey(to='machines.Interface')),
            ],
        ),
    ]
