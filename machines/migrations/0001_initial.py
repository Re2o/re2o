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
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='MachineType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='machine',
            name='type',
            field=models.ForeignKey(to='machines.MachineType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='machine',
            name='user',
            field=models.ForeignKey(to='users.User', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
