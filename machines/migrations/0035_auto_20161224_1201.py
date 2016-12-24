# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0034_iplist_need_infra'),
    ]

    operations = [
            migrations.RenameModel('Alias', 'Domain')
    ]
