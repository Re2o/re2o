# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('surname', models.CharField(max_length=255)),
                ('pseudo', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('promo', models.CharField(max_length=255)),
                ('pwd_ssha', models.CharField(max_length=255)),
                ('pwd_ntlm', models.CharField(max_length=255)),
                ('state', models.CharField(default=0, max_length=30, choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DEACTIVATED'), (2, 'STATE_ARCHIVED')])),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.School')),
            ],
        ),
    ]
