# Re2o 2.9

## Install steps

To install the latest version of Re2o, checkout the [dedicated wiki entry](https://gitlab.federez.net/re2o/re2o/-/wikis/User-Documentation/Quick-Start#update-re2o).

## Post-install steps

### MR 531: FreeRADIUS Python3 backend

On the Radius server, add `buster-backports` to your `/etc/apt/sources.list`:
```bash
echo "deb http://deb.debian.org/debian buster-backports main contrib" >> /etc/apt/sources.list
```

**Note:** If you are running Debian Bullseye, the package should already be available without going through backports.

Then install the new required packages:
```bash
apt update
apt install -t buster-backports freeradius
cat apt_requirements_radius.txt | xargs sudo apt -y install
```

### MR 582: Autocomplete light

On the Re2o server, install the new dependency and run `collectstatic`:
```bash
sudo pip3 install -r pip_requirements.txt
python3 manage.py collectstatic
```

### MR 589: Move LDAP to optional app

Add `ldap_sync` to your optional apps in your local settings (`re2o/settings_local.py`) if you want to keep using the LDAP synchronisation.

### Final steps

As usual, run the following commands after updating:
```bash
python3 manage.py migrate
python3 manage.py compilemessages
sudo service apache2 reload
```

## New features

Here is a list of noteworthy features brought by this update:

* [!488](https://gitlab.federez.net/re2o/re2o/-/merge_requests/488): Use `+` in searches to combine keywords (e.g. `John+Doe`).
* [!495](https://gitlab.federez.net/re2o/re2o/-/merge_requests/495): Add optional behavior allowing users to override another user's room, if that user is no longer active.
* [!496](https://gitlab.federez.net/re2o/re2o/-/merge_requests/496): Add option to allow users to choose their password during account creation. They will have to separately confirm their email address.
* [!504](https://gitlab.federez.net/re2o/re2o/-/merge_requests/504): Add setting to change the minimum password length.
* [!507](https://gitlab.federez.net/re2o/re2o/-/merge_requests/507): New form for editing lists of rights that should make everyone happier.
* [!512](https://gitlab.federez.net/re2o/re2o/-/merge_requests/512): Add ability to comment on tickets.
* [!513](https://gitlab.federez.net/re2o/re2o/-/merge_requests/513): IP and MAC address history (`Statistics > Machine history` tab) which also works for deleted interfaces. Uses already existing history so events before the upgrade are taken into account.
* [!516](https://gitlab.federez.net/re2o/re2o/-/merge_requests/516): Detailed events in history views (e.g. show `old_email -> new_email`).
* [!519](https://gitlab.federez.net/re2o/re2o/-/merge_requests/519): Add ability to filter event logs (e.g. to show all the subscriptions added by an admin).
* [!569](https://gitlab.federez.net/re2o/re2o/-/merge_requests/569): Refactor navbar to make menu navigation easier.
* [!569](https://gitlab.federez.net/re2o/re2o/-/merge_requests/569): Add ability to install custom themes (checkout [this repository](https://gitlab.federez.net/re2o/re2o-themes) for a list of Re2o themes).
* [!578](https://gitlab.federez.net/re2o/re2o/-/merge_requests/578) : Migrations squashed to ease the installation process.
* [!582](https://gitlab.federez.net/re2o/re2o/-/merge_requests/582): Improve autocomplete fields so they load faster and have a clearer behavior (no more entering a value without clicking and thinking it was taken into account).
* [!589](https://gitlab.federez.net/re2o/re2o/-/merge_requests/589): Move LDAP to a separate optional app.
* Plenty of bug fixes.

You can view the full list of closed issues [here](https://gitlab.federez.net/re2o/re2o/-/issues?scope=all&state=all&milestone_title=Re2o%202.9).

# Before Re2o 2.9

## MR 160: Datepicker

Install libjs-jquery libjs-jquery-ui libjs-jquery-timepicker libjs-bootstrap javascript-common
```bash
apt-get -y install \
    libjs-jquery \
    libjs-jquery-ui \
    libjs-jquery-timepicker \
    libjs-bootstrap \
    javascript-common
```
Enable javascript-common conf
```bash
a2enconf javascript-common
```

Delete old jquery files :
```bash
rm -r static_files/js/jquery-ui-*
rm static_files/js/jquery-2.2.4.min.js
rm static/css/jquery-ui-timepicker-addon.css
```

## MR 159: Graph topo & MR 164: branche de création de graph

Add a graph of the network topology
Install *graphviz*:
```
apt-get -y install graphviz
```
Create the *media/images* directory:
```
mkdir -p media/images
```

## MR 163: Fix install re2o

Refactored install_re2o.sh script.
* There are more tools available with it but some function have changed, report to [the dedicated wiki page](https://gitlab.federez.net/federez/re2o/wikis/User%20Documentation/Setup%20script)for more informations or run:
```
install_re2o.sh help
```

* The installation templates (LDIF files and `re2o/settings_locale.example.py`) have been changed to use `example.net` instead of `example.org` (more neutral and generic)

## MR 176: Add awesome Logo

Add the logo and fix somme issues on the navbar and home page. Only collecting the statics is needed:
```
python3 manage.py collectstatic
```

## MR 172: Refactor API

Creates a new (nearly) REST API to expose all models of Re2o. See [the dedicated wiki page](https://gitlab.federez.net/federez/re2o/wikis/API/Raw-Usage) for more details on how to use it.
* For testing purpose, add `volatildap` package:
```
pip3 install volatildap
```
* Activate HTTP Authorization passthrough in by adding the following in `/etc/apache2/site-available/re2o.conf` (example in `install_utils/apache2/re2o.conf`):
```
    WSGIPassAuthorization On
```
* Activate the API if you want to use it by adding `'api'` to the optional apps in `re2o/settings_local.py`:
```
OPTIONAL_APPS = (
    ...
    'api',
    ...
)
```

## MR 177: Add django-debug-toolbar support

Add the possibility to enable `django-debug-toolbar` in debug mode. First install the APT package:
```
apt install pyhton3-django-debug-toolbar
```
And then activate it for Re2o by adding the app to the `OPTIONAL_APPS` in `re2o/settings_local.py`:
```python
OPTIONAL_APPS = (
    # ...
    'debug_toolbar',
    # ...
)
```
If you to restrict the IP which can see the debug, use the `INTERNAL_IPS` options in `re2o/settings_local.py`:
```
INTERNAL_IPS = ["10.0.0.1", "10.0.0.2"]
```

## MR 145: Fix #117 : Use unix_name instead of name for ldap groups

Fix a mixing between unix_name and name for groups
After this modification you need to:
* Double-check your defined groups' unix-name only contain small letters 
* Run the following commands to rebuild your ldap's groups:
  ```shell
  python3 manage.py ldap_rebuild
  ```

* You may need to force your nslcd cache to be reloaded on some servers (else you will have to wait for the cache to be refreshed):
  ```bash
  sudo nslcd -i groups
  ```

## MR 174 : Fix online payment + allow users to pay their subscription

Add the possibility to use custom payment methods. There is also a boolean field on the 
Payments allowing every user to use some kinds of payment. You have to add the rights `cotisations.use_every_payment` and `cotisations.buy_every_article`
to the staff members so they can use every type of payment to buy anything.

Don't forget to run migrations, several settings previously in the `preferences` app ar now
in their own Payment models.

To have a closer look on how the payments works, please go to the wiki.

## MR 182: Add role models

Adds the Role model.
You need to ensure that your database character set is utf-8.
```sql
ALTER DATABASE re2o CHARACTER SET utf8;
```

## MR 247: Fix des comptes mails

Fix several issues with email accounts, you need to collect the static files.

```bash
./manage.py collectstatic
```

## MR 203 Add custom invoices

The custom invoices are now stored in database. You need to migrate your database :

```bash
python3 manage.py migrate
```

On some database engines (postgreSQL) you also need to update the id sequences:

```bash
python3 manage.py sqlsequencereset cotisations | python3 manage.py dbshell
```

## MR 296: Frontend changes

Install fonts-font-awesome

```bash
apt-get -y install fonts-font-awesome
```

Collec new statics

```bash
python3 manage.py collectstatic
```

## MR 391: Document templates and subscription vouchers

Re2o can now use templates for generated invoices. To load default templates run

```bash
./install update
```

Be carefull, you need the proper rights to edit a DocumentTemplate.

Re2o now sends subscription voucher when an invoice is controlled. It uses one
of the templates. You also need to set the name of the president of your association
to be set in your settings.

## MR 427: Tickets
Manually edit `settings_local.py` to provide the new `OPTIONNAL_APPS` lists:
```python
OPTIONNAL_APPS_RE2O = ('tickets',)
OPTIONNAL_APPS = OPTIONNAL_APPS_RE2O + (...,...,)
```

Don't forget to run migrations afterwards.

## MR 433 : upgrade django-ldapdb to 1.3.0

Uninstall the existing django-ldapdb installation

    pip3 uninstall django-ldapdb
    
Install debian(buster) supported version 

    apt install python3-django-ldapdb

If you use MySQL, please run 

```
SET GLOBAL SQL_MODE=ANSI_QUOTES;
```

## MR 531

To use the freeradius python3 backend, please add buster-backports sources to
your apt lists.

Then, install and update freeradius :
```bash
apt install -t buster-backports freeradius
apt install python3-dev
```

Make sure that all depending packages (python3-django etc) provided in the new
apt_requirements_radius.txt are installed.

## MR 535 : Routers

It is now possible to use a custom router file, if you want to have mutli database
support, with for example one as master database and one as replica database.
If you want to add a database routers, please fill in in settings_local.py 
and add your databse.
Then, add a file "local_routers.py" in folder app re2o, and add your router path 
in the settings_local.py file :

```python
LOCAL_ROUTERS = ["re2o.local_routers.DbRouter"]
```
