# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0024_machinetype_need_infra'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', models.CharField(max_length=255)),
                ('need_infra', models.BooleanField(default=False)),
                ('extension', models.ForeignKey(to='machines.Extension', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.RemoveField(
            model_name='machinetype',
            name='extension',
        ),
        migrations.RemoveField(
            model_name='machinetype',
            name='need_infra',
        ),
        migrations.AlterField(
            model_name='iplist',
            name='ip_type',
            field=models.ForeignKey(to='machines.IpType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='machinetype',
            name='ip_type',
            field=models.ForeignKey(to='machines.IpType', null=True, blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
