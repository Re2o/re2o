# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-30 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0002_foreign_keys'),
        ('preferences', '0001_model_creation'),
        ('topologie', '0001_model_creation'),
    ]
    

    operations = [
        migrations.AddField(
            model_name='building',
            name='dormitory',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='topologie.Dormitory'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='constructor',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='topologie.ConstructorSwitch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='module',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='topologie.ModuleSwitch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='switch',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='topologie.Switch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='port',
            name='custom_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='topologie.PortProfile'),
        ),
        migrations.AddField(
            model_name='port',
            name='machine_interface',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='machines.Interface'),
        ),
        migrations.AddField(
            model_name='port',
            name='related',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_port', to='topologie.Port'),
        ),
        migrations.AddField(
            model_name='port',
            name='switch',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ports', to='topologie.Switch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portprofile',
            name='on_dormitory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dormitory_ofprofil', to='topologie.Dormitory', verbose_name='profile on dormitory'),
        ),
        migrations.AddField(
            model_name='portprofile',
            name='vlan_tagged',
            field=models.ManyToManyField(blank=True, related_name='vlan_tagged', to='machines.Vlan', verbose_name='VLAN(s) tagged'),
        ),
        migrations.AddField(
            model_name='portprofile',
            name='vlan_untagged',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vlan_untagged', to='machines.Vlan', verbose_name='VLAN untagged'),
        ),
        migrations.AddField(
            model_name='switch',
            name='management_creds',
            field=models.ForeignKey(blank=True, help_text='Management credentials for the switch.', null=True, on_delete=django.db.models.deletion.PROTECT, to='preferences.SwitchManagementCred'),
        ),
        migrations.AddField(
            model_name='switch',
            name='model',
            field=models.ForeignKey(blank=True, help_text='Switch model.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='topologie.ModelSwitch'),
        ),
        migrations.AddField(
            model_name='switch',
            name='radius_key',
            field=models.ForeignKey(blank=True, help_text='RADIUS key of the switch.', null=True, on_delete=django.db.models.deletion.PROTECT, to='preferences.RadiusKey'),
        ),
        migrations.AddField(
            model_name='switch',
            name='stack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='topologie.Stack'),
        ),
        migrations.AddField(
            model_name='switch',
            name='switchbay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='topologie.SwitchBay'),
        ),
        migrations.AddField(
            model_name='switchbay',
            name='building',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='topologie.Building'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='moduleonswitch',
            unique_together=set([('slot', 'switch')]),
        ),
        migrations.AddField(
            model_name='port',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='topologie.Room'),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('switch', 'port')]),
        ),
        migrations.AlterUniqueTogether(
            name='portprofile',
            unique_together=set([('on_dormitory', 'profil_default')]),
        ),
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([('stack', 'stack_member_id')]),
        ),
        migrations.AddField(
            model_name='room',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='topologie.Building'),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('name', 'building')]),
        ),
    ]
