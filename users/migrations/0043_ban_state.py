# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0042_auto_20161126_2028")]

    operations = [
        migrations.AddField(
            model_name="ban",
            name="state",
            field=models.IntegerField(
                choices=[(0, "STATE_HARD"), (1, "STATE_SOFT"), (2, "STATE_BRIDAGE")],
                default=0,
            ),
        )
    ]
