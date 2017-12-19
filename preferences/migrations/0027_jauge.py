# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-16 04:33
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('preferences', '0026_auto_20171216_0401'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jauge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_value', models.IntegerField(blank=True, null=True)),
                ('level_percentage', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)])),
                ('comment', models.CharField(max_length=255)),
                ('objet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
