# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_remove_ldapuser_loginshell'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapuser',
            name='login_shell',
            field=ldapdb.models.fields.CharField(blank=True, db_column='loginShell', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='rezo_rez_uid',
            field=models.IntegerField(blank=True, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='uid_number',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='users.School', null=True),
        ),
    ]
