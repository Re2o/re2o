# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_permission_alias(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    for codename in ["add_alias", "change_alias", "delete_alias"]:
        # Retrieve the wrong permission
        try:
            to_remove = Permission.objects.get(
                codename=codename, content_type__model="domain"
            )
        except Permission.DoesNotExist:
            # The permission is missing so no problem
            pass
        else:
            to_remove.delete()


def remove_permission_text(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    for codename in ["add_text", "change_text", "delete_text"]:
        # Retrieve the wrong permission
        try:
            to_remove = Permission.objects.get(
                codename=codename, content_type__model="txt"
            )
        except Permission.DoesNotExist:
            # The permission is missing so no problem
            pass
        else:
            to_remove.delete()


class Migration(migrations.Migration):

    dependencies = [("machines", "0082_auto_20180525_2209")]

    operations = [
        migrations.RunPython(remove_permission_text),
        migrations.RunPython(remove_permission_alias),
    ]
