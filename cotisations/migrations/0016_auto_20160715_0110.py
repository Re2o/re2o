# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0015_auto_20160714_2142'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='cotisation',
            new_name='iscotisation',
        ),
        migrations.RenameField(
            model_name='vente',
            old_name='cotisation',
            new_name='iscotisation',
        ),
        migrations.RemoveField(
            model_name='cotisation',
            name='facture',
        ),
        migrations.AddField(
            model_name='cotisation',
            name='vente',
            field=models.OneToOneField(to='cotisations.Vente', null=True),
            preserve_default=False,
        ),
    ]
