# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20160704_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='Whitelist',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('raison', models.CharField(max_length=255)),
                ('date_start', models.DateTimeField(auto_now_add=True)),
                ('date_end', models.DateTimeField(help_text='%m/%d/%y %H:%M:%S')),
                ('user', models.ForeignKey(to='users.User', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
