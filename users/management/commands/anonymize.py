from django.core.management.base import BaseCommand
from users.models import User, School, Adherent, Club
from machines.models import Domain, Machine
from django.db.models import F, Value
from django.db.models import Q
from django.db.models.functions import Concat

from re2o.login import hashNT, makeSecret

import os, random, string
from random import randint

class Command(BaseCommand):
    help="Anonymize the data in the database in order to use them on critical servers (dev, personnal...). Every information will be overwritten using non-personnal informations. This script must follow any modification of the database.\nOptionnal argument: {id|id|id|...} to exclude users from anonymisation"

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=int, help='User ID')

    def handle(self, *args, **kwargs):
        users_ids = kwargs['user_id']
        for user_id in users_ids:
            self.stdout.write("User: {} will not be anonymised".format(User.objects.filter(id=user_id).get().name))
            
        self.stdout.write(self.style.WARNING('\nDISCLAIMER\nThis function will make your database unusable for production. Are you sure you want to run this ?(doit): '))
        if(input()=="doit"):

            total = Adherent.objects.count()
            self.stdout.write("Starting anonymizing the {} users data.".format(total))
            
            u = User.objects.filter(~Q(id__in=users_ids))
            a = Adherent.objects.filter(~Q(id__in=users_ids))
            c = Club.objects.filter(~Q(id__in=users_ids))
            d = Domain.objects.all()
            m = Machine.objects.filter(~Q(user_id__in=users_ids))

            self.stdout.write('Supression de l\'école...')
            # Create a fake School to put everyone in it.
            ecole = School(name="Ecole des Ninja")
            ecole.save()
            u.update(school=ecole)
            self.stdout.write(self.style.SUCCESS('done ...'))

            self.stdout.write('Supression des chambres...')
            a.update(room=None)
            c.update(room=None)
            self.stdout.write(self.style.SUCCESS('done ...'))

            self.stdout.write('Supression des mails...')
            u.update(email='example@example.org', 
                    local_email_redirect = False, 
                    local_email_enabled=False)
            self.stdout.write(self.style.SUCCESS('done ...'))

            self.stdout.write('Supression des noms, prenoms, pseudo, telephone, commentaire...')
            a.update(name=Concat(Value('name of '), 'id'))
            self.stdout.write(self.style.SUCCESS('done name'))

            a.update(surname=Concat(Value('surname of '), 'id'))
            self.stdout.write(self.style.SUCCESS('done surname'))

            u.update(pseudo=F('id'))
            self.stdout.write(self.style.SUCCESS('done pseudo'))

            a.update(telephone=Concat(Value('phone of '), 'id'))
            self.stdout.write(self.style.SUCCESS('done phone'))

            a.update(comment=Concat(Value('commentaire of '), 'id'))
            self.stdout.write(self.style.SUCCESS('done ...'))
            
            self.stdout.write('Renommage des machines...')
            m.update(name=Concat(Value('Machine '),F('id'),Value(' of '),F('user_id')))
            d.update(name=Concat(Value('Domaine id '),F('id')))
            self.stdout.write(self.style.SUCCESS('done ...'))

            self.stdout.write('Unification du mot de passe...')
            # Define the password
            chars = string.ascii_letters + string.digits + '!@#$%^&*()'
            taille = 20
            random.seed = (os.urandom(1024))
            password = ""
            for i in range(taille):
                password+=random.choice(chars)

            self.stdout.write(self.style.HTTP_NOT_MODIFIED('The password will be: {}'.format(password)))

            u.update(pwd_ntlm = hashNT(password))
            u.update(password = makeSecret(password))
            self.stdout.write(self.style.SUCCESS('done...'))

            self.stdout.write("Data anonymized!")

        else:
                self.stdout.write("Anonymisation aborted")
