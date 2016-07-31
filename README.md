# Re2o

## Avant propos 

Re2o est un logiciel d'administration développé initiallement au rezometz. Il se veut agnostique au réseau considéré, de manière à être installable en quelques clics.

Il utilise le framework django avec python3. Il permet de gérer les adhérents, les machines, les factures, les droits d'accès, les switchs et la topologie du réseau.
De cette manière, il est possible de pluguer très facilement des services dessus, qui accèdent à la base de donnée en passant par django (ex : dhcp), en chargeant la liste de toutes les mac-ip, ou la liste des mac-ip autorisées sur le réseau (adhérent à jour de cotisation).

## Installation

Dépendances :

Avec apt (recommandé):
 * python3-django (1.8, jessie-backports)
 * python3-django-macaddress (stretch)
 * python3-dateutil (jessie-backports)
 * texlive-latex-base (jessie)
 * texlive-fonts-recommended (jessie)
 * python3-djangorestframework (stretch)

Avec pip3:
 * django-bootstrap3 (pip install)
 * django-ldapdb

Moteur de db conseillé (mysql), postgresql fonctionne également.
Pour mysql, il faut installer :

 * mysql-server (jessie)
 * python3-mysqldb (jessie-backports)

## Configuration 

Le site est prêt a fonctionner, il faut simplement créer la base de donnée (par défaut re2o), et régler les variables présentes dans setting_local.py
Un fichier d'exemple est disponible.
Ensuite, effectuer les migrations. Un squelette de base de donnée, via un mysqldump peut être fourni.

## Mise en production avec apache

re2o/wsgi.py permet de fonctionner avec apache2 en production

## Fonctionnement avec les services

Pour charger les objets django, il suffit de faire User.objects.all() pour tous les users par exemple. 
Cependant, pour que les services fonctionnent de manière simple, des fonctions toutes prètes existent deja pour charger la liste des users autorisés à se connecter ( has_access(user)), etc. Ces fonctions sont personnalisables, et permettent un fonctionnement très simple des services.
