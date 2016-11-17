SECRET_KEY = 'SUPER_SECRET'

DB_PASSWORD = 'SUPER_SECRET'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

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

# Association information

SITE_NAME = "Re2o.rez"

LOGO_PATH = "static_files/logo.png"
ASSO_NAME = "Asso reseau"
ASSO_ADDRESS_LINE1 = "2, rue Edouard Belin"
ASSO_ADDRESS_LINE2 = "57070 Metz"
ASSO_SIRET = ""
ASSO_EMAIL = "tresorier@ecole.fr"
ASSO_PHONE = "01 02 03 04 05"

services_urls = {
#Fill IT  : ex :  'gitlab': {
#                           'url': 'https://gitlab.rezometz.org',
#                           'logo': 'gitlab.png',
#                           'description': 'Gitlab is cool 8-)'},
    }

# Number of hours a token remains valid after having been created.  Numeric and string
# versions should have the same meaning.
REQ_EXPIRE_HRS = 48
REQ_EXPIRE_STR = '48 heures'

# Email `From` field
EMAIL_FROM = 'www-data@serveur.net'

# Reglages pour la bdd ldap
LDAP = {
    'base_user_dn' : 'cn=Utilisateurs,dc=ldap,dc=example,dc=org',
    'base_userservice_dn' : 'ou=service-users,dc=ldap,dc=example,dc=org',
    'base_usergroup_dn' : 'ou=posix,ou=groups,dc=ldap,dc=example,dc=org',
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

# Main extension used in asso
MAIN_EXTENSION = ".rez"

