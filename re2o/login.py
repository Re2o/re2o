# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
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

# -*- coding: utf-8 -*-
# Module d'authentification
# David Sinquin, Gabriel Détraz, Goulven Kermarec


import hashlib
import binascii
import os
from base64 import encodestring
from base64 import decodestring
from collections import OrderedDict

from django.contrib.auth import hashers


ALGO_NAME = "{SSHA}"
ALGO_LEN = len(ALGO_NAME + "$")
DIGEST_LEN = 20


def makeSecret(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode())
    h.update(salt)
    return ALGO_NAME + "$" + encodestring(h.digest() + salt).decode()[:-1]


def hashNT(password):
    hash = hashlib.new('md4', password.encode('utf-16le')).digest()
    return binascii.hexlify(hash).upper()


def checkPassword(challenge_password, password):
    challenge_bytes = decodestring(challenge_password[ALGO_LEN:].encode())
    digest = challenge_bytes[:DIGEST_LEN]
    salt = challenge_bytes[DIGEST_LEN:]
    hr = hashlib.sha1(password.encode())
    hr.update(salt)
    valid_password = True
    # La comparaison est volontairement en temps constant
    # (pour éviter les timing-attacks)
    for i, j in zip(digest, hr.digest()):
        valid_password &= i == j
    return valid_password


class SSHAPasswordHasher(hashers.BasePasswordHasher):
    """
    SSHA password hashing to allow for LDAP auth compatibility
    """

    algorithm = ALGO_NAME

    def encode(self, password, salt, iterations=None):
        """
        Hash and salt the given password using SSHA algorithm

        salt is overridden
        """
        assert password is not None
        return makeSecret(password)

    def verify(self, password, encoded):
        """
        Check password against encoded using SSHA algorithm
        """
        assert encoded.startswith(self.algorithm)
        return checkPassword(encoded, password)

    def safe_summary(self, encoded):
        """
        Provides a safe summary ofthe password
        """
        assert encoded.startswith(self.algorithm)
        hash = encoded[ALGO_LEN:]
        hash = binascii.hexlify(decodestring(hash.encode())).decode()
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('iterations', 0),
            ('salt', hashers.mask_hash(hash[2*DIGEST_LEN:], show=2)),
            ('hash', hashers.mask_hash(hash[:2*DIGEST_LEN])),
        ])

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass
