#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Codé par PAC , forké de 20-100

""" Module pour dialoguer avec la NoteKfet2015 """

import json
import socket
import ssl
import traceback


def get_response(socket):
    length_str = b""
    char = socket.recv(1)
    while char != b"\n":
        length_str += char
        char = socket.recv(1)
    total = int(length_str)
    return json.loads(socket.recv(total).decode("utf-8"))


def connect(server, port):
    sock = socket.socket()
    try:
        # On établit la connexion sur port 4242
        sock.connect((server, port))
        # On passe en SSL
        sock = ssl.wrap_socket(sock)
        # On fait un hello
        sock.send(b'["hello", "manual"]')
        retcode = get_response(sock)
    except:
        # Si on a foiré quelque part, c'est que le serveur est down
        return (False, sock, "Serveur indisponible")
    return (True, sock, "")


def login(server, port, username, password, masque=[[], [], True]):
    result, sock, err = connect(server, port)
    if not result:
        return (False, None, err)
    try:
        commande = ["login", [username, password, "bdd", masque]]
        sock.send(json.dumps(commande).encode("utf-8"))
        response = get_response(sock)
        retcode = response["retcode"]
        if retcode == 0:
            return (True, sock, "")
        elif retcode == 5:
            return (False, sock, "Login incorrect")
        else:
            return (False, sock, "Erreur inconnue " + str(retcode))
    except:
        # Si on a foiré quelque part, c'est que le serveur est down
        return (False, sock, "Erreur de communication avec le serveur")


def don(sock, montant, id_note, facture):
    """
    Faire faire un don à l'id_note
    """
    try:
        sock.send(
            json.dumps(
                [
                    "dons",
                    [
                        [id_note],
                        round(montant * 100),
                        "Facture : id=%s, designation=%s"
                        % (facture.id, facture.name()),
                    ],
                ]
            ).encode("utf-8")
        )
        response = get_response(sock)
        retcode = response["retcode"]
        transaction_retcode = response["msg"][0][0]
        if (
            0 < retcode < 100
            or 200 <= retcode
            or 0 < transaction_retcode < 100
            or 200 <= transaction_retcode
        ):
            return (False, "Transaction échouée. (Solde trop négatif ?)")
        elif retcode == 0:
            return (True, "")
        else:
            return (False, "Erreur inconnue " + str(retcode))
    except:
        return (False, "Erreur de communication avec le serveur")
