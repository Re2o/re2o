# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_request'),
    ]

    operations = [
        migrations.CreateModel(
            name='LdapUser',
            fields=[
                ('dn', models.CharField(max_length=200)),
                ('gid', ldapdb.models.fields.IntegerField(db_column='gidNumber')),
                ('name', ldapdb.models.fields.CharField(primary_key=True, max_length=200, db_column='cn', serialize=False)),
                ('uid', ldapdb.models.fields.CharField(max_length=200, db_column='uid')),
                ('uidNumber', ldapdb.models.fields.IntegerField(unique=True, db_column='uidNumber')),
                ('sn', ldapdb.models.fields.CharField(max_length=200, db_column='sn')),
                ('loginShell', ldapdb.models.fields.CharField(default='/bin/zsh', max_length=200, db_column='loginShell')),
                ('mail', ldapdb.models.fields.CharField(max_length=200, db_column='mail')),
                ('given_name', ldapdb.models.fields.CharField(max_length=200, db_column='givenName')),
                ('home_directory', ldapdb.models.fields.CharField(max_length=200, db_column='homeDirectory')),
                ('dialupAccess', ldapdb.models.fields.CharField(max_length=200, db_column='dialupAccess')),
                ('mac_list', ldapdb.models.fields.CharField(max_length=200, db_column='radiusCallingStationId')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
