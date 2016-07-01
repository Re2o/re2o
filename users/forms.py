# -*- coding: utf-8 -*-


from django import forms


class PassForm(forms.Form):
    passwd = forms.CharField(label=u'Nouveau mot de passe', max_length=255, widget=forms.PasswordInput)
