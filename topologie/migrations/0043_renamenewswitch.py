# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-31 19:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("topologie", "0042_transferswitch")]

    operations = [migrations.RenameModel(old_name="NewSwitch", new_name="Switch")]
