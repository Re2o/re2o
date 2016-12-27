# Re2o

Gnu public license v2.0

## Avant propos 

Re2o est un logiciel d'administration développé initiallement au rezometz. Il se veut agnostique au réseau considéré, de manière à être installable en quelques clics.

Il utilise le framework django avec python3. Il permet de gérer les adhérents, les machines, les factures, les droits d'accès, les switchs et la topologie du réseau.
De cette manière, il est possible de pluguer très facilement des services dessus, qui accèdent à la base de donnée en passant par django (ex : dhcp), en chargeant la liste de toutes les mac-ip, ou la liste des mac-ip autorisées sur le réseau (adhérent à jour de cotisation).

## Installation des dépendances

L'installation comporte 3 partie : le serveur web où se trouve le depot re2o ainsi que toutes ses dépendances, le serveur bdd (mysql ou pgsql) et le serveur ldap. Ces 3 serveurs peuvent en réalité être la même machine, ou séparés (recommandé en production).
Le serveur web sera nommé serveur A, le serveur bdd serveur B et le serveur ldap serveur C.

### Prérequis sur le serveur A

Voici la liste des dépendances à installer sur le serveur principal (A).

### Avec apt :

#### Sous debian 8
Paquets obligatoires:
 * python3-django (1.8, jessie-backports)
 * python3-django-macaddress (stretch)
 * python3-dateutil (jessie-backports)
 * texlive (jessie)
 * texlive-latex-base (jessie)
 * texlive-fonts-recommended (jessie)
 * python3-djangorestframework (jessie)
 * python3-django-reversion (stretch)
 * python3-pip (jessie)

Paquet recommandés:
 * python3-django-extensions (jessie)

#### Sous debian 9

Paquets obligatoires:
 * python3-django (1.10, stretch)
 * python3-dateutil (stretch)
 * texlive (stretch)
 * texlive-latex-base (stretch)
 * texlive-fonts-recommended (strech)
 * python3-djangorestframework (stretch)
 * python3-django-reversion (stretch)
 * python3-pip (stretch)

Paquet recommandés:
 * python3-django-extensions (stretch)


### Autres dépendances : 

Avec pip3 (pip3 install):
 * django-bootstrap3
 * django-ldapdb

Moteur de db conseillé (mysql), postgresql fonctionne également.
Pour mysql, il faut installer : 
 * python3-mysqldb (jessie-backports)
 * mysql-client

### Prérequis sur le serveur B

Sur le serveur B, installer mysql ou postgresql, dans la version jessie ou stretch.
 * mysql-server (jessie/stretch) ou postgresql (jessie-stretch)

### Prérequis sur le serveur C
Sur le serveur C (ldap), avec apt :
 * slapd (jessie/stretch)

## Installation sur le serveur principal A

Cloner le dépot re2o à partir du gitlab, par exemple dans /var/www/re2o.
Ensuite, il faut créer le fichier settings_local.py dans le sous dossier re2o, un settings_local.example.py est présent. Les options sont commentées, et des options par défaut existent.

En particulier, il est nécessaire de générer un login/mdp admin pour le ldap et un login/mdp pour l'utilisateur sql (cf ci-dessous), à mettre dans settings_local.py

## Installation du serveur mysql/postgresql sur B

Sur le serveur mysql ou postgresl, il est nécessaire de créer une base de donnée re2o, ainsi qu'un user re2o et un mot de passe associé. Ne pas oublier de faire écouter le serveur mysql ou postgresql avec les acl nécessaire pour que A puisse l'utiliser.

Voici les étapes à éxecuter pour mysql :
 * CREATE DATABASE re2o;
 * CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
 * GRANT ALL PRIVILEGES ON re2o.* TO 'newuser'@'localhost';
 * FLUSH PRIVILEGES;

Si les serveurs A et B ne sont pas la même machine, il est nécessaire de remplacer localhost par l'ip avec laquelle A contacte B dans les commandes du dessus.
Une fois ces commandes effectuées, ne pas oublier de vérifier que newuser et password sont présents dans settings_local.py

### Installation du serveur ldap

Ceci se fait en plusieurs étapes : 
 * générer un login/mdp administrateur (par example mkpasswd sous debian)
 * Copier depuis re2o/install_utils (dans le dépot re2o) les fichiers db.ldiff et schema.ldiff (normalement sur le serveur A) sur le serveur C (par ex dans /tmp)
 * 
### Insérer le mot de passe dans FILL_IN du schema.ldiff et db.ldiff, en hashant le mdp à l'aide de slappasswd

### Remplacer dans schema.ldiff et db.ldiff 'dc=example,dc=org' par le suffixe de l'association

### Arréter slapd

service slapd stop

### Supprimer les données existantes

rm -rf /etc/ldap/slapd.d/*

rm -rf /var/lib/ldap/*

mkdir /var/lib/ldap/accesslog

### Ajoute les données et le schema

slapadd -n 0 -l schema.ldiff -F /etc/ldap/slapd.d/

slapadd -n 1 -l db.ldiff

chown -R openldap:openldap /etc/ldap/slapd.d

chown -R openldap:openldap /var/lib/ldap

service slapd start

## Installation du sql et démarage django

Installer mysql ou postgresql

Créer la base de donnée re2o, en créant un utilisateur re2o avec des droits sur une bdd re2o

### Créer settings_local.py à partir de settings_local.example.py

## Configuration 

Le site est prêt a fonctionner, il faut simplement créer la base de donnée (par défaut re2o), et régler les variables présentes dans setting_local.py
Un fichier d'exemple est disponible.
Ensuite, effectuer les migrations. Un squelette de base de donnée, via un mysqldump peut être fourni.

## Mise en production avec apache

re2o/wsgi.py permet de fonctionner avec apache2 en production

## Fonctionnement avec les services

Pour charger les objets django, il suffit de faire User.objects.all() pour tous les users par exemple. 
Cependant, pour que les services fonctionnent de manière simple, des fonctions toutes prètes existent deja pour charger la liste des users autorisés à se connecter ( has_access(user)), etc. Ces fonctions sont personnalisables, et permettent un fonctionnement très simple des services.
