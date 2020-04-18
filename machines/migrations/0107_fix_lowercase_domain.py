# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.exceptions import ValidationError
import logging

def fix_duplicate(apps, schema_editor):
    logger = logging.getLogger(__name__)
    db_alias = schema_editor.connection.alias
    Domain = apps.get_model("machines", "Domain")
    domains_to_fix = filter(lambda m : not m.name.islower(), Domain.objects.using(db_alias).all())
    for domain in domains_to_fix:
        try:
            domain.name = domain.name.lower()
            domain.validate_unique()
            domain.clean()
        except ValidationError:
            old_name = domain.name
            domain.name = domain.name.lower() + str(domain.interface_parent.id)
            domain.clean()
            warning_message = "Warning : Domain %s has been renamed %s due to dns uniqueness" % (old_name, domain.name)
            logger.warning(warning_message)
        domain.save()

def unfix_duplicate(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [("machines", "0106_auto_20191120_0159")]

    operations = [
        migrations.RunPython(fix_duplicate, unfix_duplicate),
    ]
