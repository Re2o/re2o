# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_remove_ldapuser_mac_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListShell',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('shell', models.CharField(unique=True, max_length=255)),
            ],
        ),
    ]
