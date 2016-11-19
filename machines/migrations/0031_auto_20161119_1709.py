# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0030_auto_20161118_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('priority', models.IntegerField(unique=True)),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='machines.Alias')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
            ],
        ),
        migrations.CreateModel(
            name='Ns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('interface', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='machines.Interface')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
            ],
        ),
        migrations.AlterField(
            model_name='iptype',
            name='domaine_ip',
            field=models.GenericIPAddressField(protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='iptype',
            name='domaine_range',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(8), django.core.validators.MaxValueValidator(32)]),
        ),
    ]
