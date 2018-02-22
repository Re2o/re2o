import string
import binascii
from random import choice
from Crypto.Cipher import AES

from django.db import models
from django.conf import settings

EOD = '`%EofD%`'  # This should be something that will not occur in strings


def genstring(length=16, chars=string.printable):
    return ''.join([choice(chars) for i in range(length)])


def encrypt(key, s):
    obj = AES.new(key)
    datalength = len(s) + len(EOD)
    if datalength < 16:
        saltlength = 16 - datalength
    else:
        saltlength = 16 - datalength % 16
    ss = ''.join([s, EOD, genstring(saltlength)])
    return obj.encrypt(ss)


def decrypt(key, s):
    obj = AES.new(key)
    ss = obj.decrypt(s)
    print(ss)
    return ss.split(bytes(EOD, 'utf-8'))[0]


class AESEncryptedField(models.CharField):
    def save_form_data(self, instance, data):
        setattr(instance, self.name,
                binascii.b2a_base64(encrypt(settings.AES_KEY, data)))

    def to_python(self, value):
        if value is None:
            return None
        return decrypt(settings.AES_KEY,
                       binascii.a2b_base64(value)).decode('utf-8')

    def from_db_value(self, value, expression, connection, *args):
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
