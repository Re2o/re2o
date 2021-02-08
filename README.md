**Note:** English version below.

# Re2o

GNU public license v2.0

## Avant propos 

Re2o est un logiciel d'administration développé initialement au [Rézo Metz](https://www.rezometz.org/). Il
se veut agnostique au réseau considéré, de manière à être installable et configurable facilement.

Il utilise le framework django avec python3. Il permet de gérer les adhérents, 
les machines, les factures, les droits d'accès, les switchs et la topologie du 
réseau.
Il est possible d'activer très facilement des services qui améliorerons les possibilités de Re2o pour convenir au mieux aux besoins de chaque association.

## Installation

Un tutoriel pour installer le projet est disponible [sur le wiki](https://gitlab.federez.net/re2o/re2o/wikis/User%20Documentation/Quick%20Start).

## Fonctionnement Général

Re2o utilise le Framework Django et suit donc le principe de toutes les applications Django. Les différents composants sont les models (qui définissent les entrées de la base de données), les templates (qui définissent les pages), les views (qui génèrent les templates avec les données pertinentes), et les forms (qui définissent les pages de modification des objets). Ce framework permet de manipuler les données comme des objets Python. 

Tous ces composants sont regroupés en apps (users, machines, topologie,...). Certaines de ces apps constituent le coeur de Re2o et sont indispensables à son fonctionnement. Certaines autres apps sont optionnelles et peuvent être activées en fonction des besoins de chaque association.

## API Rest

Les données stockées dans Re2o sont disponibles via un API Rest. Les services installés sur d'autres machines (dhcp, dns, firewall,...) utilisent cet API pour avoir accès aux données des utilisateurs et fonctionner.

# Wiki

Le [Wiki](https://gitlab.federez.net/re2o/re2o/-/wikis/home) est accessible sur le gitlab de Federez. Il regroupe les informations et instructions pour la plupart des composants de Re2o.

----

# Re2o

GNU Public license v2.0

## Foreword

Re2o is a management software initially developed at [Rézo Metz](https://www.rezometz.org/). It is now in use in several student organizations. It aims to remain agnostic of the organization that uses it and be easy to setup.

Re2o is based on the Django framework and Python3. Its core functionalities include managing the members, their machines, their invoices and their rights to the network but also the topology of the network and its devices.
On top of this, it is possible to plug services to enhance the possibilities and fit the need of each organization.

# Setup

A tutorial is available on the [Wiki](https://gitlab.federez.net/re2o/re2o/wikis/User%20Documentation/Quick%20Start) to describe the setup process.

# General Functioning

Re2o follow the general functioning of a Django project and split its components between the models (describe the database objects), the templates (that define the front end), the views (that populate and serve the templates) and the forms (that provide front end object edition/creation/removal). This framework provide an abstraction layer to manipulate SQL objects as Python objects.

Functionalities are grouped in apps (users, machines, topologie,...). Along the core functionalities, optional functionalities are available and can be activated in the preferences.

## Rest API

Re2o provide a Rest API to allow external services (dhcp, dns, firewall,...) installed on remote machines to access database informations in Json format. Those services are optional and should be installed and activated to fit each organization needs.

# Wiki

The [Wiki](https://gitlab.federez.net/re2o/re2o/-/wikis/home) is available to provide information and instruction for most components of Re2o.
