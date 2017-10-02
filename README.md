# Re2o

Gnu public license v2.0

## Avant propos 

Re2o est un logiciel d'administration développé initiallement au rezometz. Il
se veut agnostique au réseau considéré, de manière à être installable en 
quelques clics.

Il utilise le framework django avec python3. Il permet de gérer les adhérents, 
les machines, les factures, les droits d'accès, les switchs et la topologie du 
réseau.
De cette manière, il est possible de pluguer très facilement des services 
dessus, qui accèdent à la base de donnée en passant par django (ex : dhcp), en 
chargeant la liste de toutes les mac-ip, ou la liste des mac-ip autorisées sur 
le réseau (adhérent à jour de cotisation).

#Installation

## Installation des dépendances

L'installation comporte 3 partie : le serveur web où se trouve le depot re2o
ainsi que toutes ses dépendances, le serveur bdd (mysql ou pgsql) et le 
serveur ldap. Ces 3 serveurs peuvent en réalité être la même machine, ou séparés
(recommandé en production).
Le serveur web sera nommé serveur A, le serveur bdd serveur B et le serveur ldap
serveur C.

### Prérequis sur le serveur A

Voici la liste des dépendances à installer sur le serveur principal (A).

### Avec apt :

#### Sous debian 9

Paquets obligatoires:
 * python3-django (1.10, stretch)
 * python3-dateutil (stretch)
 * texlive-latex-base (stretch)
 * texlive-fonts-recommended (strech)
 * python3-djangorestframework (stretch)
 * python3-django-reversion (stretch)
 * python3-pip (stretch)

Paquet recommandés:
 * python3-django-extensions (stretch)


### Autres dépendances : 

Paquets préalables à installer avec apt : 
 * libsasl2-dev (stable)
 * libldap2-dev (stable)
 * libssl-dev (stable)

Avec pip3 (pip3 install):
 * django-bootstrap3
 * django-ldapdb
 * django-macaddress

Moteur de db conseillé (mysql), postgresql fonctionne également.
Pour mysql, il faut installer : 
 * python3-mysqldb
 * mysql-client

### Prérequis sur le serveur B

Sur le serveur B, installer mysql ou postgresql, dans la version stretch.
 * mysql-server (stretch) ou postgresql (stretch)

### Prérequis sur le serveur C
Sur le serveur C (ldap), avec apt :
 * slapd (stretch)

### Installation sur le serveur principal A

Cloner le dépot re2o à partir du gitlab, par exemple dans /var/www/re2o.
Ensuite, il faut créer le fichier settings_local.py dans le sous dossier re2o, 
un settings_local.example.py est présent. Les options sont commentées, et des 
options par défaut existent.

En particulier, il est nécessaire de générer un login/mdp admin pour le ldap et 
un login/mdp pour l'utilisateur sql (cf ci-dessous), à mettre dans 
settings_local.py

### Installation du serveur mysql/postgresql sur B

Sur le serveur mysql ou postgresl, il est nécessaire de créer une base de 
donnée re2o, ainsi qu'un user re2o et un mot de passe associé. 
Ne pas oublier de faire écouter le serveur mysql ou postgresql avec les acl 
nécessaire pour que A puisse l'utiliser.

Voici les étapes à éxecuter pour mysql :
 * CREATE DATABASE re2o collate='utf8_general_ci';
 * CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
 * GRANT ALL PRIVILEGES ON re2o.* TO 'newuser'@'localhost';
 * FLUSH PRIVILEGES;

Si les serveurs A et B ne sont pas la même machine, il est nécessaire de 
remplacer localhost par l'ip avec laquelle A contacte B dans les commandes 
du dessus.
Une fois ces commandes effectuées, ne pas oublier de vérifier que newuser et 
password sont présents dans settings_local.py

### Installation du serveur ldap sur le serveur C

Ceci se fait en plusieurs étapes : 
 * générer un login/mdp administrateur (par example mkpasswd sous debian)
 * Copier depuis re2o/install_utils (dans le dépot re2o) les fichiers db.ldiff 
et schema.ldiff (normalement sur le serveur A) sur le serveur C 
(par ex dans /tmp)
 * Hasher le mot de passe généré en utilisant la commande slappasswd 
(installée par slapd)
 * Remplacer toutes les sections FILL_IN par le hash dans schema.ldiff et 
db.ldiff
 * Remplacer dans schema.ldiff et db.ldiff 'dc=example,dc=org' par le 
suffixe de l'organisation
 * Arréter slapd
 * Supprimer les données existantes : '''rm -rf /etc/ldap/slapd.d/*''' et 
'''rm -rf /var/lib/ldap/*'''
 * Injecter le nouveau schéma : 
'''slapadd -n 0 -l schema.ldiff -F /etc/ldap/slapd.d/''' et 
'''slapadd -n 1 -l db.ldiff'''
 * Réparer les permissions (chown -R openldap:openldap /etc/ldap/slapd.d et
chown -R openldap:openldap /var/lib/ldap) puis relancer slapd

Normalement le serveur ldap démare et est fonctionnel. 
Par défaut tls n'est pas activé, il faut pour cela modifier le schéma pour 
indiquer l'emplacement du certificat.
Pour visualiser et éditer le ldap, l'utilisation de shelldap est fortement
recommandée, en utilisant en binddn cn=admin,dc=ldap,dc=example,dc=org et 
binddpw le mot de passe admin.

## Configuration initiale

Normalement à cette étape, le ldap et la bdd sql sont configurées correctement.

Il faut alors lancer dans le dépot re2o '''python3 manage.py migrate''' qui
va structurer initialement la base de données.
Les migrations sont normalement comitées au fur et à mesure, néanmoins cette
étape peut crasher, merci de reporter les bugs.

## Démarer le site web

Il faut utiliser un moteur pour servir le site web. Nginx ou apache2 sont 
recommandés.
Pour apache2 :
 * apt install apache2
 * apt install libapache2-mod-wsgi-py3 (pour le module wsgi)

Un example de site apache2 se trouve dans install_utils ( re2o.conf)
re2o/wsgi.py permet de fonctionner avec apache2 en production

## Configuration avancée

Une fois démaré, le site web devrait être accessible. 
Pour créer un premier user, faire '''python3 manage.py createsuperuser''' 
qui va alors créer un user admin.
Il est conseillé de créer alors les droits cableur, bureau, trésorier et infra, 
qui n'existent pas par défaut dans le menu adhérents.
Il est également conseillé de créer un user portant le nom de
l'association/organisation, qui possedera l'ensemble des machines.

## Installations Optionnelles
### Générer le schéma des dépendances

Pour cela : 
 * apt install python3-django-extensions
 * python3 manage.py graph_models -a -g -o re2o.png

# Fonctionnement interne

## Fonctionnement général

Re2o est séparé entre les models, qui sont visible sur le schéma des 
dépendances. Il s'agit en réalité des tables sql, et les fields etant les 
colonnes.
Ceci dit il n'est jamais nécessaire de toucher directement au sql, django 
procédant automatiquement à tout cela. 
On crée donc différents models (user, right pour les droits des users, 
interfaces, IpList pour l'ensemble des adresses ip, etc)

Du coté des forms, il s'agit des formulaire d'édition des models. Il 
s'agit de ModelForms django, qui héritent des models très simplement, voir la 
documentation django models forms.

Enfin les views, générent les pages web à partir des forms et des templates.

## Fonctionnement avec les services

Les services dhcp.py, dns.py etc accèdent aux données via des vues rest.
Celles-ci se trouvent dans machines/views.py. Elles sont générées via 
machines/serializers.py qui génère les vues. IL s'agit de vues en json utilisées
par re2o-tools pour récupérer les données.
Il est nécessaire de créer un user dans re2o avec le droit serveur qui permet 
d'accéder à ces vues, utilisé par re2o-tools.

# Requète en base de donnée

Pour avoir un shell, il suffit de lancer '''python3 manage.py shell'''
Pour charger des objets, example avec User, faire : 
''' from users.models import User'''
Pour charger les objets django, il suffit de faire User.objects.all() 
pour tous les users par exemple. 
Il est ensuite aisé de faire des requètes, par exemple 
User.objects.filter(pseudo='test')
Des exemples et la documentation complète sur les requètes django sont 
disponible sur le site officiel.
