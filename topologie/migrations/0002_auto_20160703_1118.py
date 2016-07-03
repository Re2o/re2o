# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('topologie', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('port', models.IntegerField()),
                ('details', models.CharField(max_length=255, blank=True)),
                ('_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('_content_type', models.ForeignKey(null=True, blank=True, to='contenttypes.ContentType')),
                ('switch', models.ForeignKey(related_name='ports', to='topologie.Switch')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('_content_type', '_object_id')]),
        ),
    ]
