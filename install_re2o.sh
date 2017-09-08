#!/bin/bash

setup_ldap() {
	apt-get -y install slapd

	echo "Hashage du mot de passe ldap..."
	hashed_ldap_passwd=$(slappasswd -s $1)

	echo $hashed_ldap_passwd
	echo "Formatage des fichiers de config ldap"
	sed 's|dc=example,dc=org|'"$2"'|g' install_utils/db.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/db
	sed 's|dc=example,dc=org|'"$2"'|g' install_utils/schema.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/schema

	echo "Destruction config ldap existante"
	service slapd stop
	rm -rf /etc/ldap/slapd.d/*
	rm -rf /var/lib/ldap/*

	echo "Ecriture de la configuration actuelle"
	slapadd -n 0 -l /tmp/schema -F /etc/ldap/slapd.d/
	slapadd -n 1 -l /tmp/db

	echo "Reparation des permissions et redémarage de slapd"
	chown -R openldap:openldap /etc/ldap/slapd.d
	chown -R openldap:openldap /var/lib/ldap
	service slapd start
}


install_re2o_server() {
echo "Installation de Re2o ! 
Cet utilitaire va procéder à l'installation initiale de re2o. Le serveur présent doit être vierge.
Preconfiguration..."

export DEBIAN_FRONTEND=noninteractive

apt-get -y install dialog

HEIGHT=15
WIDTH=40
CHOICE_HEIGHT=4
BACKTITLE="Preconfiguration re2o"
MENU="Choisir une option"

TITLE="Choix du moteur bdd"
OPTIONS=(1 "mysql"
         2 "postgresql")

sql_bdd_type=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear


TITLE="Extension locale (ex : example.org)"

extension_locale=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear

IFS='.' read -a extension_locale_array <<< $extension_locale


for i in "${extension_locale_array[@]}"
do
    ldap_dn+="dc=$i,"
done
ldap_dn=${ldap_dn::-1}
echo $ldap_dn

TITLE="Emplacement de la bdd"
OPTIONS=(1 "Local"
         2 "Distant")

sql_is_local=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear

TITLE="Mot de passe sql"

sql_password=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear


if [ $sql_is_local == 2 ]
then 
TITLE="Login sql"
sql_login=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
TITLE="Nom de la bdd sql"
sql_name=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
TITLE="Hote de la base de donnée"
sql_host=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
else
sql_name="re2o"
sql_login="re2o"
sql_host="localhost"
fi

sql_command="CREATE DATABASE $sql_name collate='utf8_general_ci';
CREATE USER '$sql_login'@'localhost' IDENTIFIED BY '$sql_password';
GRANT ALL PRIVILEGES ON $sql_name.* TO '$sql_login'@'localhost';
FLUSH PRIVILEGES;"


TITLE="Emplacement du ldap"
OPTIONS=(1 "Local"
         2 "Distant")

ldap_is_local=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

echo "Vous devrez fournir un login/host dans le cas où le ldap est non local"

TITLE="Mot de passe ldap"
ldap_password=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
if [ $ldap_is_local == 2 ]
then 
TITLE="Cn ldap admin"
ldap_cn=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
TITLE="Hote ldap"
ldap_host=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
else
ldap_cn="cn=admin,"
ldap_cn+=$ldap_dn
ldap_host="localhost"
fi


TITLE="Hôte pour l'envoi de mail"
email_host=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)

TITLE="Port du serveur mail"
OPTIONS=(25 "25 (SMTP)"
         465 "465 (SMTPS)"
	 587 "587 (Submission)")

email_port=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)
clear
if [ $ldap_is_local == 2 ]
then 
TITLE="Cn ldap admin"
ldap_cn=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
TITLE="Hote ldap"
ldap_host=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
else
ldap_cn="cn=admin,"
ldap_cn+=$ldap_dn
ldap_host="localhost"
fi


echo "Installation des paquets de base"
apt-get -y install python3-django python3-dateutil texlive-latex-base texlive-fonts-recommended python3-djangorestframework python3-django-reversion python3-pip libsasl2-dev libldap2-dev libssl-dev
pip3 install django-bootstrap3
pip3 install django-ldapdb
pip3 install django-macaddress

if [ $sql_bdd_type == 1 ]
then
    if [ $sql_is_local == 1 ]
    then
    apt-get -y install mysql-server
    mysql -u root --execute="$sql_command"
    else
    echo "Veuillez saisir la commande suivante sur le serveur sql distant, puis validez"
    echo $sql_command
    while true; do
	read -p "Continue (y/n)?" choice
	case "$choice" in 
	y|Y ) break;;
	n|N ) exit;;
	* ) echo "invalid";;
	esac
    done
    fi
    apt-get -y install python3-mysqldb mysql-client
    else
    if [ $sql_is_local == 1 ]
    then
    apt-get -y install postgresql-server
    fi
    apt-get -y install postgresql-client
fi 

if [ $ldap_is_local == 1 ]
then

setup_ldap $ldap_password $ldap_dn

else
echo "Vous devrez manuellement effectuer les opérations de setup de la base ldap sur le serveurs distant.
Lancez la commande : ./install_re2o.sh ldap $ldap_password $ldap_dn"
fi

echo "Ecriture de settings_local"

django_secret_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(50)]))")

cp re2o/settings_local.example.py re2o/settings_local.py
sed -i 's/SUPER_SECRET_KEY/'"$django_secret_key"'/g' re2o/settings_local.py
sed -i 's/SUPER_SECRET_DB/'"$sql_password"'/g' re2o/settings_local.py
sed -i 's/db_name_value/'"$sql_name"'/g' re2o/settings_local.py
sed -i 's/db_user_value/'"$sql_login"'/g' re2o/settings_local.py
sed -i 's/db_host_value/'"$sql_host"'/g' re2o/settings_local.py
sed -i 's/ldap_dn/'"$ldap_cn"'/g' re2o/settings_local.py
sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' re2o/settings_local.py
sed -i 's/ldap_host_ip/'"$ldap_host"'/g' re2o/settings_local.py
sed -i 's/dc=example,dc=org/'"$ldap_dn"'/g' re2o/settings_local.py
sed -i 's/example.org/'"$extension_locale"'/g' re2o/settings_local.py
sed -i 's/MY_EMAIL_HOST/'"$email_host"'/g' re2o/settings_local.py
sed -i 's/MY_EMAIL_PORT/'"$email_port"'/g' re2o/settings_local.py

echo "Application des migrations"
python3 manage.py migrate

echo "Collecte des statics"
python3 manage.py collectstatic

BACKTITLE="Fin de l'installation"
TITLE="Serveur web à utiliser"
OPTIONS=(1 "apache2"
         2 "nginx")

web_serveur=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear

TITLE="Url où servir le serveur web (ex : re2o.example.org)"
url_server=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear

TITLE="Utiliser tls et générer automatiquement le certificat LE ?"
OPTIONS=(1 "Oui"
         2 "Non")

is_tls=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear

sed -i 's/URL_SERVER/'"$url_server"'/g' re2o/settings_local.py


if [ $web_serveur == 1 ]
then
apt-get -y install apache2 libapache2-mod-wsgi-py3
a2enmod ssl
if [ $is_tls == 1 ]
then
cp install_utils/apache2/re2o-tls.conf /etc/apache2/sites-available/re2o.conf
apt-get -y install certbot
apt-get -y install python-certbot-apache
certbot certonly --rsa-key-size 4096 --apache -d $url_server
sed -i 's/LE_PATH/'"$url_server"'/g' /etc/apache2/sites-available/re2o.conf
else
cp install_utils/apache2/re2o.conf /etc/apache2/sites-available/re2o.conf
fi
rm /etc/apache2/sites-enabled/000-default.conf
sed -i 's|URL_SERVER|'"$url_server"'|g' /etc/apache2/sites-available/re2o.conf
current_path=$(pwd)
sed -i 's|PATH|'"$current_path"'|g' /etc/apache2/sites-available/re2o.conf
a2ensite re2o
service apache2 reload
else
echo "Nginx non supporté, vous devrez installer manuellement"
fi

python3 manage.py createsuperuser

}

main_function() {
if [ ! -z "$1" ]
then
if [ $1 == ldap ]
then
if [ ! -z "$2" ] 
then
echo Installation du ldap
setup_ldap $2 $3
else
echo Arguments invalides !
exit
fi
fi
else
install_re2o_server
fi
}

main_function $1 $2 $3
