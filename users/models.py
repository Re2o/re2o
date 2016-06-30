from django.db import models
from django.forms import ModelForm

class User(models.Model):
    STATE_ACTIVE = 0
    STATE_DEACTIVATED = 1
    STATE_ARCHIVED = 2
    STATES = (
            (0, 'STATE_ACTIVE'),
            (1, 'STATE_DEACTIVATED'),
            (2, 'STATE_ARCHIVED'),
            )

    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    pseudo = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    school = models.ForeignKey('School', on_delete=models.PROTECT)
    promo = models.CharField(max_length=255)
    pwd_ssha = models.CharField(max_length=255)
    pwd_ntlm = models.CharField(max_length=255)
    #location = models.ForeignKey('Location', on_delete=models.SET_DEFAULT)
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class InfoForm(ModelForm):
    class Meta:
        model = User
        fields = ['name','surname','pseudo','email', 'school', 'promo']

class PasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['pwd_ssha','pwd_ntlm']

class ArchiveForm(ModelForm):
    class Meta:
        model = User
        fields = ['state']

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']
