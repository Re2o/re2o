from django.core.management.base import BaseCommand, CommandError

from datetime import datetime, timedelta
from pytz

from users.models import User

UTC = pytz.timezone('UTC')

class Command(BaseCommand):
    commands = ['email_remainder',]
    args = '[command]'
    help = 'Send email remainders'

    def handle(self, *args, **options):
        '''
        Sends an email before the end of a user's subscription
        '''
        users = User.objects.filter(state="STATE_ACTIVE")

        for user in users:
            remaining = user.end_adhesion() - datetime.today(tz=UTC)
            if (timedelta(weeks=4) - remaining).days == 1:
                4_weeks_reminder()
            elif (timedelta(weeks=1) - remaining).days == 1:
                week_reminder()
            elif remaining.days == 1:
                last_day_reminder()

def month_reminder():
    pass

