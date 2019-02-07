# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-09-19 20:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0094_auto_20180815_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='arp_protect',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='dhcp_snooping',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='dhcpv6_snooping',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='igmp',
            field=models.BooleanField(default=False, help_text='Gestion multicast v4'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='mld',
            field=models.BooleanField(default=False, help_text='Gestion multicast v6'),
        ),
    ]
