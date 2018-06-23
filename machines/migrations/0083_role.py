# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-23 14:07
from __future__ import unicode_literals

from django.db import migrations, models
import re2o.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0082_auto_20180621_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type', models.CharField(max_length=255, unique=True)),
                ('servers', models.ManyToManyField(to='machines.Interface')),
            ],
            options={
                'permissions': (('view_role', 'Peut voir un objet service'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
    ]
