from django.db import models
from django.forms import ModelForm
from django import forms

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
        return self.pseudo

class Right(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT) 
    right = models.ForeignKey('ListRight', on_delete=models.PROTECT)
    
    class Meta:
        unique_together = ("user", "right")

    def __str__(self):
        return str(self.user) + " - " + str(self.right)

class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class ListRight(models.Model):
    listright = models.CharField(max_length=255)

    def __str__(self):
        return self.listright

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(InfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom'
        self.fields['surname'].label = 'Prenom'
        self.fields['school'].label = 'Etablissement'

    class Meta:
        model = User
        fields = '__all__'

class InfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(InfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom'
        self.fields['surname'].label = 'Prenom'
        self.fields['school'].label = 'Etablissement'

    class Meta:
        model = User
        fields = ['name','surname','pseudo','email', 'school', 'promo']

class PasswordForm(ModelForm):
    class Meta:
        model = User
        fields = ['pwd_ssha','pwd_ntlm']

class StateForm(ModelForm):
    class Meta:
        model = User
        fields = ['state']

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']

class RightForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RightForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Utilisateur'
        self.fields['right'].label = 'Droit'

    class Meta:
        model = Right
        fields = ['user', 'right']

class DelRightForm(ModelForm):
    rights = forms.ModelMultipleChoiceField(queryset=Right.objects.all(), label="Droits actuels",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Right
        exclude = ['user', 'right']

