import os
import random
import string
from random import randint

from django.core.management.base import BaseCommand
from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from reversion.models import Revision

from machines.models import Domain, Machine
from re2o.login import hashNT, makeSecret
from users.models import Adherent, Club, School, User


class Command(BaseCommand):
    help = "Anonymise the data in the database in order to use them on critical servers (dev, personal...). Every information will be overwritten using non-personal information. This script must follow any modification of the database.\nOptional argument: {id|id|id|...} to exclude users from anonymisation."

    def add_arguments(self, parser):
        parser.add_argument("user_id", nargs="+", type=int, help="User ID")

    def handle(self, *args, **kwargs):
        users_ids = kwargs["user_id"]
        for user_id in users_ids:
            self.stdout.write(
                "User: {} will not be anonymised.".format(
                    User.objects.filter(id=user_id).get().name
                )
            )

        self.stdout.write(
            self.style.WARNING(
                "\nDISCLAIMER\nThis function will make your database unusable for production. Are you sure you want to run this? (doit): "
            )
        )
        if input() == "doit":

            total = Adherent.objects.count()
            self.stdout.write("Starting anonymizing the {} users data.".format(total))

            u = User.objects.filter(~Q(id__in=users_ids))
            a = Adherent.objects.filter(~Q(id__in=users_ids))
            c = Club.objects.filter(~Q(id__in=users_ids))
            d = Domain.objects.all()
            m = Machine.objects.filter(~Q(user_id__in=users_ids))

            self.stdout.write("Deletion of the school...")
            # Create a fake School to put everyone in it.
            ecole = School(name="Ninja School")
            ecole.save()
            u.update(school=ecole)
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write("Deletion of rooms...")
            a.update(room=None)
            c.update(room=None)
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write("Deletion of email addresses...")
            u.update(
                email="example@example.org",
                local_email_redirect=False,
                local_email_enabled=False,
            )
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write(
                "Deletion of first names, surnames, usernames, telephone numbers, comments..."
            )
            a.update(name=Concat(Value("First name of "), "id"))
            self.stdout.write(self.style.SUCCESS("Done for first names..."))

            a.update(surname=Concat(Value("Surname of "), "id"))
            self.stdout.write(self.style.SUCCESS("Done for surnames..."))

            u.update(pseudo=F("id"))
            self.stdout.write(self.style.SUCCESS("Done for usernames..."))

            a.update(telephone=Concat(Value("Telephone number of "), "id"))
            self.stdout.write(self.style.SUCCESS("Done for telephone numbers..."))

            a.update(comment=Concat(Value("Comment of "), "id"))
            self.stdout.write(self.style.SUCCESS("Done for comments..."))

            self.stdout.write("Renaming of machines...")
            m.update(
                name=Concat(Value("Machine "), F("id"), Value(" of "), F("user_id"))
            )
            d.update(name=Concat(Value("Domain id "), F("id")))
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write("Unification of the password...")
            # Define the password
            chars = string.ascii_letters + string.digits + "!@#$%^&*()"
            taille = 20
            random.seed = os.urandom(1024)
            password = ""
            for i in range(taille):
                password += random.choice(chars)

            self.stdout.write(
                self.style.HTTP_NOT_MODIFIED(
                    "The password will be: {}.".format(password)
                )
            )

            u.update(pwd_ntlm=hashNT(password))
            u.update(password=makeSecret(password))
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write("Deletion of the history (this may take some time)...")
            Revision.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Done..."))

            self.stdout.write("Data anonymised!")

        else:
            self.stdout.write("Anonymisation aborted!")
