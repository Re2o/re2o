# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import macaddress.fields


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6')),
                ('mac_address', macaddress.fields.MACAddressField(integer=True)),
                ('details', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpList',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ipv4', models.GenericIPAddressField(protocol='IPv4')),
            ],
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv4',
            field=models.OneToOneField(null=True, to='machines.IpList', blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='interface',
            name='machine',
            field=models.ForeignKey(to='machines.Machine', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
