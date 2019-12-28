# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0043_auto_20161224_1156")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="ssh_public_key",
            field=models.CharField(max_length=2047, null=True, blank=True),
        )
    ]
