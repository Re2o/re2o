# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import machines.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0015_auto_20160707_0105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(unique=True, max_length=255, validators=[machines.models.full_domain_validator], help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points"),
        ),
        migrations.AddField(
            model_name='machinetype',
            name='extension',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, to='machines.Extension'),
        ),
    ]
