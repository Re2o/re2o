# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_auto_20160726_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapuser',
            name='display_name',
            field=ldapdb.models.fields.CharField(null=True, blank=True, max_length=200, db_column='displayName'),
        ),
        migrations.AddField(
            model_name='ldapuser',
            name='macs',
            field=ldapdb.models.fields.ListField(null=True, blank=True, max_length=200, db_column='radiusCallingStationId'),
        ),
        migrations.AddField(
            model_name='ldapuser',
            name='sambat_nt_password',
            field=ldapdb.models.fields.CharField(null=True, blank=True, max_length=200, db_column='sambaNTPassword'),
        ),
        migrations.AddField(
            model_name='ldapuser',
            name='user_password',
            field=ldapdb.models.fields.CharField(null=True, blank=True, max_length=200, db_column='userPassword'),
        ),
        migrations.AddField(
            model_name='listright',
            name='gid',
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='shell',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=1, to='users.ListShell'),
        ),
    ]
