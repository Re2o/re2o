## Datepicker

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
