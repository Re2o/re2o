from django.core.management.base import BaseCommand
from users.models import User, School, Adherent
from django.db.models import F, Value
from django.db.models.functions import Concat

class Command(BaseCommand):
    help="Anonymize the data in the database in order to use them on critical servers (dev, personnal...). Every information will be overwritten using non-personnal informations. This script must follow any modification of the database." 

    def handle(self, *args, **kwargs):

        total = User.objects.count()
        self.stdout.write("Starting anonymizing the {} users data.".format(total))
        
        u = User.objects.all()
        a = Adherent.objects.all()

        self.stdout.write('Supression de l\'école...')
        # Create a fake School to put everyone in it.
        ecole = School(name="Ecole des Ninja")
        ecole.save()
        u.update(school=ecole)
        self.stdout.write(self.style.SUCCESS('done ...'))

        self.stdout.write('Supression des chambres...')
        a.update(room=None)
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

        a.update(pseudo=F('id'))
        self.stdout.write(self.style.SUCCESS('done pseudo'))

        a.update(telephone=Concat(Value('phone of '), 'id'))
        self.stdout.write(self.style.SUCCESS('done phone'))

        a.update(comment=Concat(Value('commentaire of '), 'id'))
        self.stdout.write(self.style.SUCCESS('done ...'))
        

        self.stdout.write("Data anonymized!")
