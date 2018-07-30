# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-29 14:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


class Migration(migrations.Migration):

    def create_initial_local_email_account(apps, schema_editor):
        db_alias = schema_editor.connection.alias
        User = apps.get_model("users", "User")
        LocalEmailAccount = apps.get_model("users", "LocalEmailAccount")
        users = User.objects.using(db_alias).all()
        for user in users:
            LocalEmailAccount.objects.using(db_alias).create(
                local_part=user.pseudo,
                user=user
            )

    def delete_all_local_email_accounts(apps, schema_editor):
        db_alias = schema_editor.connection.alias
        LocalEmailAccount = apps.get_model("users", "LocalEmailAccount")
        LocalEmailAccount.objects.using(db_alias).delete()

    dependencies = [
        ('users', '0072_auto_20180426_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalEmailAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_part', models.CharField(help_text="Local part of the email address", max_length=128, unique=True)),
                ('user', models.ForeignKey(help_text='User of the local email', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
            options={'permissions': (('view_localemailaccount', 'Can see a local email account object'),), 'verbose_name': 'Local email account', 'verbose_name_plural': 'Local email accounts'},
        ),
        migrations.AddField(
            model_name='user',
            name='local_email_enabled',
            field=models.BooleanField(default=False, help_text="Wether or not to enable the local email account."),
        ),
        migrations.AddField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False, help_text='Whether or not to redirect the local email messages to the main email.'),
        ),
        migrations.RunPython(create_initial_local_email_account,
                             delete_all_local_email_accounts),
        ),
    ]

