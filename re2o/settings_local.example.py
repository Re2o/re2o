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

SECRET_KEY = 'SUPER_SECRET'

DB_PASSWORD = 'SUPER_SECRET'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ADMINS = [('Example', 'rezo-admin@example.org')]

SERVER_EMAIL = 'no-reply@example.org'

# Obligatoire, liste des host autorisés
ALLOWED_HOSTS = ['test.example.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 're2o',
        'USER': 're2o',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://10.0.0.0/',
        'USER': 'cn=admin,dc=ldap,dc=example,dc=org',
        'PASSWORD': 'SUPER_SECRET',
     }
}

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_AGE = 60 * 60 * 3

# Association information

SITE_NAME = "Re2o.rez"

# Main extension used in asso
MAIN_EXTENSION = ".rez"

LOGO_PATH = "static_files/logo.png"

# Number of hours a token remains valid after having been created.  Numeric and string
# versions should have the same meaning.
REQ_EXPIRE_HRS = 48
REQ_EXPIRE_STR = '48 heures'

# Email `From` field
EMAIL_FROM = 'www-data@serveur.net'

EMAIL_HOST = 'smtp.example.org'

# Reglages pour la bdd ldap
LDAP = {
    'base_user_dn' : 'cn=Utilisateurs,dc=ldap,dc=example,dc=org',
    'base_userservice_dn' : 'ou=service-users,dc=ldap,dc=example,dc=org',
    'base_usergroup_dn' : 'ou=posix,ou=groups,dc=ldap,dc=example,dc=org',
    'base_userservicegroup_dn' : 'ou=services,ou=groups,dc=ldap,dc=example,dc=org',
    'user_gid' : 500,
    }


UID_RANGES = {
    'users' : [21001,30000],
    'service-users' : [20000,21000],
}

# Chaque groupe a un gid assigné, voici la place libre pour assignation
GID_RANGES = {
    'posix' : [501, 600],
}

# Liste des vlans id disponible sur un switch
VLAN_ID_LIST = [7,8,42,69]

# Décision radius à prendre
RADIUS_VLAN_DECISION = {
    'VLAN_NOK' : 42,
    'VLAN_OK' : 69,
}

OPTIONNAL_APPS = ()

