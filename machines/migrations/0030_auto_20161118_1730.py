# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0029_iptype_domaine_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='alias',
            name='extension',
            field=models.ForeignKey(to='machines.Extension', default=1, on_delete=django.db.models.deletion.PROTECT),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alias',
            name='alias',
            field=models.CharField(max_length=255, help_text='Obligatoire et unique, ne doit pas comporter de points'),
        ),
        migrations.AlterUniqueTogether(
            name='alias',
            unique_together=set([('alias', 'extension')]),
        ),
    ]
