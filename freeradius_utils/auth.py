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

# ⁻*- mode: python; coding: utf-8 -*-
"""
Backend python pour freeradius.

Ce fichier contient la définition de plusieurs fonctions d'interface à
freeradius qui peuvent être appelées (suivant les configurations) à certains
moment de l'authentification, en WiFi, filaire, ou par les NAS eux-mêmes.

Inspirés d'autres exemples trouvés ici :
https://github.com/FreeRADIUS/freeradius-server/blob/master/src/modules/rlm_python/
"""

import logging
import netaddr
import radiusd # Module magique freeradius (radiusd.py is dummy)
import os
import binascii
import hashlib
import subprocess

import os, sys
from ast import literal_eval as make_tuple

#: Serveur radius de test (pas la prod)
TEST_SERVER = bool(os.getenv('DBG_FREERADIUS', False))


## -*- Logging -*-

class RadiusdHandler(logging.Handler):
    """Handler de logs pour freeradius"""

    def emit(self, record):
        """Process un message de log, en convertissant les niveaux"""
        if record.levelno >= logging.WARN:
            rad_sig = radiusd.L_ERR
        elif record.levelno >= logging.INFO:
            rad_sig = radiusd.L_INFO
        else:
            rad_sig = radiusd.L_DBG
        radiusd.radlog(rad_sig, record.msg)

# Initialisation d'un logger (pour logguer unifié)
logger = logging.getLogger('auth.py')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')
handler = RadiusdHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

def radius_event(fun):
    """Décorateur pour les fonctions d'interfaces avec radius.
    Une telle fonction prend un uniquement argument, qui est une liste de tuples
    (clé, valeur) et renvoie un triplet dont les composantes sont :
     * le code de retour (voir radiusd.RLM_MODULE_* )
     * un tuple de couples (clé, valeur) pour les valeurs de réponse (accès ok
       et autres trucs du genre)
     * un tuple de couples (clé, valeur) pour les valeurs internes à mettre à
       jour (mot de passe par exemple)

    On se contente avec ce décorateur (pour l'instant) de convertir la liste de
    tuples en entrée en un dictionnaire."""

    def new_f(auth_data):
        if type(auth_data) == dict:
            data = auth_data
        else:
            data = dict()
            for (key, value) in auth_data or []:
                # Beware: les valeurs scalaires sont entre guillemets
                # Ex: Calling-Station-Id: "une_adresse_mac"
                data[key] = value.replace('"', '')
        try:
            # TODO s'assurer ici que les tuples renvoyés sont bien des (str,str)
            # rlm_python ne digère PAS les unicodes
            return fun(data)
        except Exception as err:
            logger.error('Failed %r on data %r' % (err, auth_data))
            raise

    return new_f

   

@radius_event
def instantiate(*_):
    """Utile pour initialiser les connexions ldap une première fois (otherwise,
    do nothing)"""
    logger.info('Instantiation')
    if TEST_SERVER:
        logger.info('DBG_FREERADIUS is enabled')

@radius_event
def authorize(data):
    """Fonction qui aiguille entre nas, wifi et filaire pour authorize
    On se contecte de faire une verification basique de ce que contien la requète
    pour déterminer la fonction à utiliser"""
    if data.get('Service-Type', '')==u'NAS-Prompt-User' or data.get('Service-Type', '')==u'Administrative-User':
        return authorize_user(data)
    else:
        return authorize_fil(data)

@radius_event
def authorize_user(data):
    nas = data.get('NAS-IP-Address', None)
    nas_id = data.get('NAS-Identifier', None)
    user = data.get('User-Name', None)
    password = data.get('User-Password', None)
    out = subprocess.check_output(['/usr/bin/python3', '/var/www/re2o/freeradius_utils/authenticate_user.py', user, password])
    if out[:-1] == u"TRUE":
        if data.get('Service-Type', '')==u'NAS-Prompt-User':
            logger.info(u"Access of user %s on %s (%s)" % (user, nas, nas_id))
        elif data.get('Service-Type', '')==u'Administrative-User':
            logger.info(u"Enable manager for %s on %s (%s)" % (user, nas, nas_id))
        return (radiusd.RLM_MODULE_UPDATED,
            (),
            (
              ("Auth-Type", "Accept"),
            ),
            )
    else:
        return (radiusd.RLM_MODULE_UPDATED,
            (),
            (
              ("Auth-Type", "Reject"),
            ),
            )


@radius_event
def authorize_fil(data):
    """
    Check le challenge chap, et accepte.
    """

    return (radiusd.RLM_MODULE_UPDATED,
	(),
        (
          ("Auth-Type", "Accept"),
        ),
      )

@radius_event
def post_auth(data):
    # On cherche quel est le type de machine, et quel sites lui appliquer
    if data.get('NAS-Port-Type', '')==u'Ethernet':
       return post_auth_fil(data)
    elif u"Wireless" in data.get('NAS-Port-Type', ''):
       return post_auth_wifi(data)

@radius_event
def post_auth_wifi(data):
    """Appelé une fois que l'authentification est ok.
    On peut rajouter quelques éléments dans la réponse radius ici.
    Comme par exemple le vlan sur lequel placer le client"""

    port, vlan_name, reason = decide_vlan(data, True)
    mac = data.get('Calling-Station-Id', None)

    log_message = '(wifi) %s -> %s [%s%s]' % \
      (port, mac, vlan_name, (reason and u': ' + reason).encode('utf-8'))
    logger.info(log_message)

    # Si NAS ayant des mapping particuliers, à signaler ici
    vlan_id = config.vlans[vlan_name]

    # WiFi : Pour l'instant, on ne met pas d'infos de vlans dans la réponse
    # les bornes wifi ont du mal avec cela
    if WIFI_DYN_VLAN:
        return (radiusd.RLM_MODULE_UPDATED,
            (
                ("Tunnel-Type", "VLAN"),
                ("Tunnel-Medium-Type", "IEEE-802"),
                ("Tunnel-Private-Group-Id", '%d' % vlan_id),
            ),
            ()
        )

    return radiusd.RLM_MODULE_OK

@radius_event
def post_auth_fil(data):
    """Idem, mais en filaire.
    """

    nas = data.get('NAS-IP-Address', data.get('NAS-Identifier', None))
    port = data.get('NAS-Port-Id', data.get('NAS-Port', None))
    mac = data.get('Calling-Station-Id', None)
    # Hack, à cause d'une numérotation cisco baroque
    port = port.split(".")[0].split('/')[-1][-2:]
    out = subprocess.check_output(['/usr/bin/python3', '/var/www/re2o/freeradius_utils/authenticate_filaire.py', nas, port, mac])
    sw_name, reason, vlan_id = make_tuple(out)

    log_message = '(fil) %s -> %s [%s%s]' % \
      (sw_name + u":" + port, mac, vlan_id, (reason and u': ' + reason).encode('utf-8'))
    logger.info(log_message)

    # Filaire
    return (radiusd.RLM_MODULE_UPDATED,
        (
            ("Tunnel-Type", "VLAN"),
            ("Tunnel-Medium-Type", "IEEE-802"),
            ("Tunnel-Private-Group-Id", '%d' % int(vlan_id)),
        ),
        ()
    )

@radius_event
def dummy_fun(_):
    """Do nothing, successfully. (C'est pour avoir un truc à mettre)"""
    return radiusd.RLM_MODULE_OK

def detach(_=None):
    """Appelé lors du déchargement du module (enfin, normalement)"""
    print "*** goodbye from auth.py ***"
    return radiusd.RLM_MODULE_OK

