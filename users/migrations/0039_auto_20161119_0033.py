# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20161031_0258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapserviceuser',
            name='dn',
            field=models.CharField(serialize=False, max_length=200, primary_key=True),
        ),
        migrations.AlterField(
            model_name='ldapuser',
            name='dn',
            field=models.CharField(serialize=False, max_length=200, primary_key=True),
        ),
        migrations.AlterField(
            model_name='ldapusergroup',
            name='dn',
            field=models.CharField(serialize=False, max_length=200, primary_key=True),
        ),
    ]
