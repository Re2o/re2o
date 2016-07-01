# -*- coding: utf-8 -*-
# Module d'authentification
# David Sinquin, Gabriel Détraz, Goulven Kermarec

import hashlib, binascii
import os
from base64 import urlsafe_b64encode as encode
from base64 import urlsafe_b64decode as decode

def makeSecret(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode())
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt).decode()

def hashNT(password):
    hash = hashlib.new('md4', password.encode()).digest()
    return binascii.hexlify(hash)

def checkPassword(challenge_password, password):
    challenge_bytes = decode(challenge_password[6:])
    digest = challenge_bytes[:20]
    salt = challenge_bytes[20:]
    hr = hashlib.sha1(password.encode())
    hr.update(salt)
    valid_password = True
    # La comparaison est volontairement en temps constant (pour éviter les timing-attacks)
    for i, j in zip(digest, hr.digest()):
        valid_password &= i == j
    return valid_password
