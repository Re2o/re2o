# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations 
from django.conf import settings

def create_api_permission(apps, schema_editor):
    """Creates the 'use_api' permission if not created.

    The 'use_api' is a fake permission in the sense it is not associated with an
    existing model and this ensure the permission is created.
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    api_content_type, created = ContentType.objects.get_or_create(
        app_label=settings.API_CONTENT_TYPE_APP_LABEL,
        model=settings.API_CONTENT_TYPE_MODEL,
    )
    if created:
        api_content_type.save()
    api_permission, created = Permission.objects.get_or_create(
        name=settings.API_PERMISSION_NAME,
        content_type=api_content_type,
        codename=settings.API_PERMISSION_CODENAME,
    )
    if created:
        api_permission.save()

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
            migrations.RunPython(create_api_permission)
            ]
