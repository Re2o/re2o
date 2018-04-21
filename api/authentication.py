import datetime
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        token_duration = datetime.timedelta(
            seconds=settings.API_TOKEN_DURATION
        )
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if token.created < utc_now - token_duration:
            raise exceptions.AuthenticationFailed(_('Token has expired'))

        return (token.user, token)
