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

# Installation

Un tutoriel pour installer le projet est disponible [sur le wiki](https://gitlab.federez.net/federez/re2o/wikis/User%20Documentation/Quick%20Start).

# Installations Optionnelles
## Générer le schéma des dépendances

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
