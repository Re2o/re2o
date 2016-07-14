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
    }
}

# Association information

LOGO_PATH = "static_files/logo.png"
ASSO_NAME = "Asso reseau"
ASSO_ADDRESS_LINE1 = "2, rue Edouard Belin"
ASSO_ADDRESS_LINE2 = "57070 Metz"
ASSO_SIRET = ""
ASSO_EMAIL = "tresorier@ecole.fr"
ASSO_PHONE = "01 02 03 04 05"
