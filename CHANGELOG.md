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
* There are more tools available with it but some fucntion have changed, report to [the dedicated wiki page](for more informations) or run:
```
install_re2o.sh help
```
* The installation templates (LDIF files and `re2o/settings_locale.example.py`) have been changed to use `example.net` instead of `example.org` (more neutral and generic)



## MR XXX: Cleanup and refactor API

Activate HTTP Authorization passthrough in by adding the following in /etc/apache2/site-available/re2o.conf (example in install_utils/apache2/re2o.conf):
```
    WSGIPassAuthorization On
```

