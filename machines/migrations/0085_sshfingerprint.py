# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-29 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0084_dname'),
    ]

    operations = [
        migrations.CreateModel(
            name='SshFp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_key_entry', models.TextField(help_text='SSH public key', max_length=2048)),
                ('algo', models.CharField(choices=[('ssh-rsa', 'ssh-rsa'), ('ssh-ed25519', 'ssh-ed25519'), ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp256'), ('ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp384'), ('ecdsa-sha2-nistp521', 'ecdsa-sha2-nistp521')], max_length=32)),
                ('comment', models.CharField(blank=True, help_text='Comment', max_length=255, null=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines.Machine')),
            ],
            options={
                'verbose_name': 'SSHFP record',
                'verbose_name_plural': 'SSHFP records',
                'permissions': (('view_sshfp', 'Can see an SSHFP record'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
    ]
