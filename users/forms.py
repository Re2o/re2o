# -*- coding: utf-8 -*-


from django import forms


class PassForm(forms.Form):
    passwd1 = forms.CharField(label=u'Nouveau mot de passe', max_length=255, widget=forms.PasswordInput)
    passwd2 = forms.CharField(label=u'Saisir à nouveau le mot de passe', max_length=255, widget=forms.PasswordInput)
