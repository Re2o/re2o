## MR 160: Datepicker

Install libjs-jquery libjs-jquery-ui libjs-jquery-timepicker libjs-bootstrap javascript-common
```
apt-get -y install \
    libjs-jquery \
    libjs-jquery-ui \
    libjs-jquery-timepicker \
    libjs-bootstrap \
    javascript-common
```
Enable javascript-common conf
```
a2enconf javascript-common
```

Delete old jquery files :
```
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

## MR 174 : Fix online payment + allow users to pay their subscription

Add the possibility to use custom payment methods. There is also a boolean field on the 
Payments allowing every user to use some kinds of payment. You have to add the rights `cotisations.use_every_payment` and `cotisations.buy_every_article`
to the staff members so they can use every type of payment to buy anything.

Don't forget to run migrations, several settings previously in the `preferences` app ar now
in their own Payment models.

To have a closer look on how the payments works, pleas go to the wiki.
