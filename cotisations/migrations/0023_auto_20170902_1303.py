# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-02 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0022_auto_20170824_0128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paiement',
            name='type_paiement',
            field=models.IntegerField(choices=[(0, 'Autre'), (1, 'Chèque')], default=0),
        ),
    ]
