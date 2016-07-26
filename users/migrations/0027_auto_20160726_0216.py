# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_user_shell'),
    ]

    operations = [
        migrations.CreateModel(
            name='LdapUserGroup',
            fields=[
                ('dn', models.CharField(max_length=200)),
                ('gid', ldapdb.models.fields.IntegerField(db_column='gidNumber')),
                ('members', ldapdb.models.fields.ListField(db_column='memberUid', blank=True)),
                ('name', ldapdb.models.fields.CharField(db_column='cn', primary_key=True, serialize=False, max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
