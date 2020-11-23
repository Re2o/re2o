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
"""re2o.settings_locale
The file with all the available options for a locale configuration of re2o
"""

from __future__ import unicode_literals

# Should the server run in debug mode ?
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# The time zone the server is runned in
TIME_ZONE = "Europe/Paris"

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

# A range of UID to use. Used in linux environement
UID_RANGES = {"users": [21001, 30000], "service-users": [20000, 21000]}

# A range of GID to use. Used in linux environement
GID_RANGES = {"posix": [501, 600]}

# If you want to add a database routers, please fill in above and add your databse.
# Then, add a file "local_routers.py" in folder app re2o, and add your router path in
# the LOCAL_ROUTERS var as "re2o.local_routers.DbRouter". You can also add extra routers. 
LOCAL_ROUTERS = []

# Some optionnal Re2o Apps
OPTIONNAL_APPS_RE2O = ()

# Some Django apps you want to add in you local project
OPTIONNAL_APPS = OPTIONNAL_APPS_RE2O + ()

#Set auth password validator
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ['surname', 'pseudo', 'name', 'email'],
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
