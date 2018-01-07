# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-07 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0067_serveurpermission'),
    ]

    def transfer_permissions(apps, schema_editor):
        critical_rights = ['adm', 'admin', 'bureau', 'infra', 'tresorier', 'serveur', 'bofh']
        db_alias = schema_editor.connection.alias
        rights = apps.get_model("users", "ListRight")
        for right in critical_rights:
            rg = rights.objects.using(db_alias).filter(unix_name=right).first()
            rg.critical=True
            rg.save()

    def untransfer_permissions(apps, schema_editor):
        return

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('change_user_password', "Peut changer le mot de passe d'un user"), ('change_user_state', "Peut éditer l'etat d'un user"), ('change_user_force', 'Peut forcer un déménagement'), ('change_user_shell', "Peut éditer le shell d'un user"), ('change_user_groups', "Peut éditer les groupes d'un user ! Permission critique"), ('change_all_users', 'Peut éditer tous les users, y compris ceux dotés de droits. Superdroit'), ('view_user', 'Peut voir un objet user quelquonque'))},
        ),
        migrations.AddField(
            model_name='listright',
            name='critical',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(transfer_permissions, untransfer_permissions),
    ]
