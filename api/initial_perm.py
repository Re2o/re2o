from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.conf import settings

api_content_type, created = ContentType.objects.get_or_create(
    app_label=settings.API_CONTENT_TYPE_APP_LABEL,
    model=settings.API_CONTENT_TYPE_MODEL
)
if created:
    api_content_type.save()
api_permission, created = Permission.objects.get_or_create(
    name=settings.API_PERMISSION_NAME,
    content_type=api_content_type,
    codename=settings.API_PERMISSION_CODENAME
)
if created:
    api_permission.save()
