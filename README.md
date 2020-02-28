**Note:** English version below.

# Re2o

GNU public license v2.0

## Avant propos 

Re2o est un logiciel d'administration développé initialement au rezometz. Il
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

Re2o est séparé entre les models, qui sont visibles sur le schéma des
dépendances. Il s'agit en réalité des tables sql, et les fields étant les
colonnes.
Ceci dit il n'est jamais nécessaire de toucher directement au sql, django 
procédant automatiquement à tout cela. 
On crée donc différents models (user, right pour les droits des users, 
interfaces, IpList pour l'ensemble des adresses ip, etc)

Du coté des forms, il s'agit des formulaires d'édition des models. Il
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

Pour avoir un shell, lancer :
```.bash
python3 manage.py shell
```

Pour charger des objets (exemple avec User), faire :
```.python
from users.models import User
```

Pour charger les objets django, il suffit de faire `User.objects.all()`
pour tous les users par exemple.
Il est ensuite aisé de faire des requêtes, par exemple
`User.objects.filter(pseudo='test')`

Des exemples et la documentation complète sur les requêtes django sont
disponible sur le site officiel.

----

# Re2o

GNU Public license v2.0

## Foreword

Re2o is a management software initialy developed at [rezometz](https://www.rezometz.org/). It is now in use in several student organizations. It aims to remain agnostic of the organization that uses it and be easy to setup.

Re2o is based on the Django framework and Python3. It's core functionalities includes managing the members, their machines, their invoices and their access to the network but also the topology of the network and its devices.
On top of this, it is possible to plug services to enhance the possibilities and fit the need of each organization.

# Setup

A tutorial is available on the [Wiki](https://gitlab.federez.net/federez/re2o/wikis/User%20Documentation/Quick%20Start) to describe the setup process.

# General Functioning

Re2o follow the general functioning of a Django project and split its components between the models (describe the database objects), the templates (that define the front end), the views (that populate and serve the templates) and the forms (that provide front end object edition/creation/removal). This framework provide an abstraction layer to manipulate SQL objects as Python objects.

Functionalities are grouped in apps (users, machines, topologie,...). Along the core functionalities, optional functionalities are available and can be activated in the preferences.

## Rest API

Re2o provide a Rest API to allow external services (dhcp, dns, firewall,...) installed on remote machines to access database informations in Json format. Those services are optional and should be installed and activated to fit each organization needs.

# Wiki

The [Wiki](https://gitlab.federez.net/federez/re2o/-/wikis/home) is available to provide information and instruction for most components of Re2o.
