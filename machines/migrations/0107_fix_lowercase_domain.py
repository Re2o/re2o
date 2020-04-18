# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.exceptions import ValidationError

def fix_duplicate(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    domain = apps.get_model("machines", "Domain")
    machines_to_fix = list(filter(lambda m : not m.name.islower(), domain.objects.using(db_alias).all()))
    for machine in machines_to_fix:
        try:
            machine.name = machine.name.lower()
            machine.validate_unique()
            machine.clean()
        except ValidationError:
            machine.name = machine.name.lower() + str(machine.interface_parent.id)
            machine.clean() 
        machine.save()

def unfix_duplicate(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [("machines", "0106_auto_20191120_0159")]

    operations = [
        migrations.RunPython(fix_duplicate, unfix_duplicate),
    ]
