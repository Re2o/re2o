# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cotisations', '0012_auto_20160704_0118'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
                ('cotisation', models.BooleanField()),
                ('duration', models.IntegerField(null=True, blank=True, help_text='Durée exprimée en mois entiers')),
            ],
        ),
        migrations.RemoveField(
            model_name='facture',
            name='name',
        ),
        migrations.RemoveField(
            model_name='facture',
            name='prix',
        ),
        migrations.AddField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(to='cotisations.Facture', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
