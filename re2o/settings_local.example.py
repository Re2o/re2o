# coding: utf-8
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
"""re2o.settings_local
The file with all the available options for a locale configuration of re2o
"""

from __future__ import unicode_literals

# A secret key used by the server.
SECRET_KEY = "SUPER_SECRET_KEY"

# The password to access the project database
DB_PASSWORD = "SUPER_SECRET_DB"

# AES key for secret key encryption.
# The length must be a multiple of 16
AES_KEY = "A_SECRET_AES_KEY"

# Should the server run in debug mode ?
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# A list of admins of the services. Receive mails when an error occurs
ADMINS = [("Example", "admin@example.net")]

# The list of hostname the server will respond to.
ALLOWED_HOSTS = ["URL_SERVER"]

# The time zone the server is runned in
TIME_ZONE = "Europe/Paris"

# The storage systems parameters to use
DATABASES = {
    "default": {  # The DB
        "ENGINE": "db_engine",
        "NAME": "db_name_value",
        "USER": "db_user_value",
        "PASSWORD": DB_PASSWORD,
        "HOST": "db_host_value",
        "TEST": {"CHARSET": "utf8", "COLLATION": "utf8_general_ci"},
    },
    "ldap": {  # The LDAP
        "ENGINE": "ldapdb.backends.ldap",
        "NAME": "ldap://ldap_host_ip/",
        "USER": "ldap_dn",
        "TLS": True,
        "PASSWORD": "SUPER_SECRET_LDAP",
    },
}

# Security settings for secure https
# Activate once https is correctly configured
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

# The validity duration of session cookies, in seconds
SESSION_COOKIE_AGE = 60 * 60 * 3

# The path where your organization logo is stored
LOGO_PATH = "static_files/logo.png"

# The mail configuration for Re2o to send mails
SERVER_EMAIL = "no-reply@example.net"  # The mail address to use
EMAIL_HOST = "MY_EMAIL_HOST"  # The host to use
EMAIL_PORT = MY_EMAIL_PORT  # The port to use

# Settings of the LDAP structure
LDAP = {
    "base_user_dn": "cn=Utilisateurs,dc=example,dc=net",
    "base_userservice_dn": "ou=service-users,dc=example,dc=net",
    "base_usergroup_dn": "ou=posix,ou=groups,dc=example,dc=net",
    "base_userservicegroup_dn": "ou=services,ou=groups,dc=example,dc=net",
    "user_gid": 500,
}

# A range of UID to use. Used in linux environement
UID_RANGES = {"users": [21001, 30000], "service-users": [20000, 21000]}

# A range of GID to use. Used in linux environement
GID_RANGES = {"posix": [501, 600]}

# Default gid
DEFAULT_GID = 500

# If you want to add a database routers, please fill in above and add your databse.
# Then, add a file "local_routers.py" in folder app re2o, and add your router path in
# the LOCAL_ROUTERS var as "re2o.local_routers.DbRouter". You can also add extra routers.
# To use ldap you need to add "ldapdb.router.Router"
LOCAL_ROUTERS = []

# Some optionnal Re2o Apps
OPTIONNAL_APPS_RE2O = ()

# Some Django apps you want to add in you local project
OPTIONNAL_APPS = OPTIONNAL_APPS_RE2O + ()

# Some optinnal link for the navbar in a tuple (link,class,text)
OPTIONNAL_LINK_RE2O = ()

# Add statiffiles dir that were installed using system packaging
# Example to reproduce re2o2.9 behavior
# SYSTEM_STATICFILES_DIRS = ("/usr/share/fonts-font-awesome/", "/usr/share/javascript/")
SYSTEM_STATICFILES_DIRS = ()

# Wether to use CDN to retrieve bootstrap, font-aweseome and jquery files
# Default to False
USE_CDN = False

# Set auth password validator
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ["surname", "pseudo", "name", "email"],
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
