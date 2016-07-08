# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_passwords(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for row in User.objects.all():
        row.password = row.pwd_ssha
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20160706_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, blank=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(verbose_name='password', default='!', max_length=128),
            preserve_default=False,
        ),
        migrations.RunPython(
            move_passwords,
            reverse_code=migrations.RunPython.noop),
    ]
