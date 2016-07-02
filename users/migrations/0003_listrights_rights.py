# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20160630_2301'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListRights',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('listright', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rights',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('right', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.ListRights')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.User')),
            ],
        ),
    ]
