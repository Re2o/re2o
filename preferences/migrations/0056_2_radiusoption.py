# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-10-13 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


def create_radius_policy(apps, schema_editor):
    OptionalTopologie = apps.get_model('preferences', 'OptionalTopologie')
    RadiusOption = apps.get_model('preferences', 'RadiusOption')

    option,_ = OptionalTopologie.objects.get_or_create()

    radius_option = RadiusOption()
    radius_option.radius_general_policy = option.radius_general_policy
    radius_option.vlan_decision_ok = option.vlan_decision_ok

    radius_option.save()

def revert_radius(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0095_auto_20180919_2225'),
        ('preferences', '0055_generaloption_main_site_url'),
        ('preferences', '0056_1_radiusoption'),
    ]

    operations = [
        migrations.RunPython(create_radius_policy, revert_radius),
    ]
