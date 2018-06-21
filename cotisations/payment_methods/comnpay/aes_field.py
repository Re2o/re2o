# coding:utf-8
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Maël Kervella
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# App de gestion des machines pour re2o
# Gabriel Détraz, Augustin Lemesle
# Gplv2
"""preferences.aes_field
Module defining a AESEncryptedField object that can be used in forms
to handle the use of properly encrypting and decrypting AES keys
"""

import string
import binascii
from random import choice
from Crypto.Cipher import AES

from django.db import models
from django.conf import settings

EOD = '`%EofD%`'  # This should be something that will not occur in strings


def genstring(length=16, chars=string.printable):
    """ Generate a random string of length `length` and composed of
    the characters in `chars` """
    return ''.join([choice(chars) for i in range(length)])


def encrypt(key, s):
    """ AES Encrypt a secret `s` with the key `key` """
    obj = AES.new(key)
    datalength = len(s) + len(EOD)
    if datalength < 16:
        saltlength = 16 - datalength
    else:
        saltlength = 16 - datalength % 16
    ss = ''.join([s, EOD, genstring(saltlength)])
    return obj.encrypt(ss)


def decrypt(key, s):
    """ AES Decrypt a secret `s` with the key `key` """
    obj = AES.new(key)
    ss = obj.decrypt(s)
    return ss.split(bytes(EOD, 'utf-8'))[0]


class AESEncryptedField(models.CharField):
    """ A Field that can be used in forms for adding the support
    of AES ecnrypted fields """
    def save_form_data(self, instance, data):
        setattr(instance, self.name,
                binascii.b2a_base64(encrypt(settings.AES_KEY, data)))

    def to_python(self, value):
        if value is None:
            return None
        return decrypt(settings.AES_KEY,
                       binascii.a2b_base64(value)).decode('utf-8')

    def from_db_value(self, value, *args, **kwargs):
        if value is None:
            return value
        return decrypt(settings.AES_KEY,
                       binascii.a2b_base64(value)).decode('utf-8')

    def get_prep_value(self, value):
        if value is None:
            return value
        return binascii.b2a_base64(encrypt(
            settings.AES_KEY,
            value
        ))
