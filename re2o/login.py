# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au Rézo Metz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Lara Kermarec
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
# David Sinquin, Gabriel Détraz, Lara Kermarec
"""re2o.login
Module in charge of handling the login process and verifications
"""

import binascii
import crypt
import hashlib
import os
from base64 import b64decode, b64encode, decodebytes, encodebytes
from collections import OrderedDict
from hmac import compare_digest as constant_time_compare

from django.contrib.auth import hashers
from django.contrib.auth.backends import ModelBackend

ALGO_NAME = "{SSHA}"
ALGO_LEN = len(ALGO_NAME + "$")
DIGEST_LEN = 20


def makeSecret(password):
    """Build a hashed and salted version of the password with SSHA

    Parameters:
    password (string): Password to hash

     Returns:
    string: Hashed password
    """
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode())
    h.update(salt)
    return ALGO_NAME + "$" + encodebytes(h.digest() + salt).decode()[:-1]


def hashNT(password):
    """Build a md4 hash of the password to use as the NT-password

    Parameters:
    password (string): Password to hash

     Returns:
    string: Hashed password

    """
    hash_str = hashlib.new("md4", password.encode("utf-16le")).digest()
    return binascii.hexlify(hash_str).upper()


def checkPassword(challenge_password, password):
    """Check if a given password match the hash of a stored password

    Parameters:
        challenge_password (string): Password to verify with hash
        password (string): Hashed password to verify

    Returns:
        boolean: True if challenge_password and password match

    """
    challenge_bytes = decodebytes(challenge_password[ALGO_LEN:].encode())
    digest = challenge_bytes[:DIGEST_LEN]
    salt = challenge_bytes[DIGEST_LEN:]
    hr = hashlib.sha1(password.encode())
    hr.update(salt)
    return constant_time_compare(digest, hr.digest())


def hash_password_salt(hashed_password):
    """Extract the salt from a given hashed password

    Parameters:
        hashed_password (string): Hashed password to extract salt

    Returns:
        string: Salt of the password

    """
    if hashed_password.upper().startswith("{CRYPT}"):
        hashed_password = hashed_password[7:]
        if hashed_password.startswith("$"):
            return "$".join(hashed_password.split("$")[:-1])
        else:
            return hashed_password[:2]
    elif hashed_password.upper().startswith("{SSHA}"):
        try:
            digest = b64decode(hashed_password[6:])
        except TypeError as error:
            raise ValueError("b64 error for `hashed_password`: %s." % error)
        if len(digest) < 20:
            raise ValueError("`hashed_password` too short.")
        return digest[20:]
    elif hashed_password.upper().startswith("{SMD5}"):
        try:
            digest = b64decode(hashed_password[7:])
        except TypeError as error:
            raise ValueError("b64 error for `hashed_password`: %s." % error)
        if len(digest) < 16:
            raise ValueError("`hashed_password` too short.")
        return digest[16:]
    else:
        raise ValueError(
            "`hashed_password` should start with '{SSHA}' or '{CRYPT}' or '{SMD5}'."
        )


class CryptPasswordHasher(hashers.BasePasswordHasher):
    """
    Crypt password hashing to allow for LDAP auth compatibility
    We do not encode, this should bot be used !
    The actual implementation may depend on the OS.
    """

    algorithm = "{crypt}"

    def encode(self, password, salt):
        pass

    def verify(self, password, encoded):
        """
        Check password against encoded using CRYPT algorithm
        """
        assert encoded.startswith(self.algorithm)
        salt = hash_password_salt(encoded)
        return constant_time_compare(
            self.algorithm + crypt.crypt(password, salt), encoded
        )

    def safe_summary(self, encoded):
        """
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[7:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict(
            [
                ("algorithm", self.algorithm),
                ("iterations", 0),
                ("salt", hashers.mask_hash(hash_str[2 * DIGEST_LEN :], show=2)),
                ("hash", hashers.mask_hash(hash_str[: 2 * DIGEST_LEN])),
            ]
        )

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class MD5PasswordHasher(hashers.BasePasswordHasher):
    """
    Salted MD5 password hashing to allow for LDAP auth compatibility
    We do not encode, this should bot be used !
    """

    algorithm = "{SMD5}"

    def encode(self, password, salt):
        pass

    def verify(self, password, encoded):
        """
        Check password against encoded using SMD5 algorithm
        """
        assert encoded.startswith(self.algorithm)
        salt = hash_password_salt(encoded)
        return constant_time_compare(
            self.algorithm
            + "$"
            + b64encode(hashlib.md5(password.encode() + salt).digest() + salt).decode(),
            encoded,
        )

    def safe_summary(self, encoded):
        """
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[7:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict(
            [
                ("algorithm", self.algorithm),
                ("iterations", 0),
                ("salt", hashers.mask_hash(hash_str[2 * DIGEST_LEN :], show=2)),
                ("hash", hashers.mask_hash(hash_str[: 2 * DIGEST_LEN])),
            ]
        )

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class SSHAPasswordHasher(hashers.BasePasswordHasher):
    """
    Salted SHA-1 password hashing to allow for LDAP auth compatibility
    """

    algorithm = ALGO_NAME

    def encode(self, password, salt):
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
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[ALGO_LEN:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict(
            [
                ("algorithm", self.algorithm),
                ("iterations", 0),
                ("salt", hashers.mask_hash(hash_str[2 * DIGEST_LEN :], show=2)),
                ("hash", hashers.mask_hash(hash_str[: 2 * DIGEST_LEN])),
            ]
        )

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class RecryptBackend(ModelBackend):
    """Function for legacy users. During auth, if their hash password is different from SSHA or ntlm
    password is empty, rehash in SSHA or NTLM

    Returns:
        model user instance: Instance of the user logged

    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # we obtain from the classical auth backend the user
        user = super(RecryptBackend, self).authenticate(
            request, username, password, **kwargs
        )
        if user:
            if not (user.pwd_ntlm):
                # if we dont have NT hash, we create it
                user.pwd_ntlm = hashNT(password)
                user.save()
            if not ("SSHA" in user.password):
                # if the hash is too old, we update it
                user.password = makeSecret(password)
                user.save()
        return user
