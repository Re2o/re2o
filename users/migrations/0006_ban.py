# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20160702_0006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('raison', models.CharField(max_length=255)),
                ('date_start', models.DateTimeField(help_text='%m/%d/%y %H:%M:%S')),
                ('date_end', models.DateTimeField(help_text='%m/%d/%y %H:%M:%S')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.User')),
            ],
        ),
    ]
