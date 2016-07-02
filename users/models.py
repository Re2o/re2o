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
    state = models.IntegerField(choices=STATES, default=STATE_ACTIVE)
    registered = models.DateTimeField(auto_now_add=True)

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

class Ban(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    raison = models.CharField(max_length=255)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(help_text='%m/%d/%y %H:%M:%S')    

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)

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

class BanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BanForm, self).__init__(*args, **kwargs)
        self.fields['date_end'].label = 'Date de fin'

    class Meta:
        model = Ban
        exclude = ['user']
