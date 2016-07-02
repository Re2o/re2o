# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20160702_0006'),
        ('cotisations', '0007_auto_20160702_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cotisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date_start', models.DateTimeField(auto_now_add=True)),
                ('date_end', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='cotisation',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='facture',
            field=models.ForeignKey(to='cotisations.Facture', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='user',
            field=models.ForeignKey(to='users.User', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
