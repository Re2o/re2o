# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-09 16:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0061_portprofile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='portprofile',
            options={'permissions': (('view_port_profile', 'Can view a port profile object'),), 'verbose_name': 'Port profile', 'verbose_name_plural': 'Port profiles'},
        ),
        migrations.AddField(
            model_name='portprofile',
            name='name',
            field=models.CharField(default='Sans nom', max_length=255, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='hotspot_default',
            field=models.BooleanField(verbose_name='Hotspot default'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='orga_machine_default',
            field=models.BooleanField(verbose_name='Organisation machine default'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='radius_mode',
            field=models.CharField(choices=[('STRICT', 'STRICT'), ('COMMON', 'COMMON')], max_length=32, verbose_name='RADIUS mode'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='radius_type',
            field=models.CharField(choices=[('NO', 'NO'), ('802.1X', '802.1X'), ('MAC-radius', 'MAC-radius')], max_length=32, verbose_name='RADIUS type'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='room_default',
            field=models.BooleanField(verbose_name='Room default'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='uplink_default',
            field=models.BooleanField(verbose_name='Uplink default'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='vlan_tagged',
            field=models.ManyToManyField(related_name='vlan_tagged', to='machines.Vlan', verbose_name='VLAN(s) tagged'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='vlan_untagged',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vlan_untagged', to='machines.Vlan', verbose_name='VLAN untagged'),
        ),
    ]
