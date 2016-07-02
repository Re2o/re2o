# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20160702_0006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Banque',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('cheque', models.CharField(max_length=255)),
                ('number', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
                ('article', models.ForeignKey(to='cotisations.Article', on_delete=django.db.models.deletion.PROTECT)),
                ('banque', models.ForeignKey(to='cotisations.Banque', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('moyen', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='facture',
            name='paiement',
            field=models.ForeignKey(to='cotisations.Paiement', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='facture',
            name='user',
            field=models.ForeignKey(to='users.User', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
