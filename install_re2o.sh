#!/bin/bash

setup_ldap() {
	apt-get -y install slapd

	echo "Hashing the LDAP password..."
	hashed_ldap_passwd=$(slappasswd -s $1)

	echo $hashed_ldap_passwd
	echo "Building the LDAP config files"
	sed 's|dc=example,dc=org|'"$2"'|g' install_utils/db.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/db
	sed 's|dc=example,dc=org|'"$2"'|g' install_utils/schema.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/schema

	echo "Deleting exisitng LDAP configuration"
	service slapd stop
	rm -rf /etc/ldap/slapd.d/*
	rm -rf /var/lib/ldap/*

	echo "Setting up the new LDAP configuration"
	slapadd -n 0 -l /tmp/schema -F /etc/ldap/slapd.d/
	slapadd -n 1 -l /tmp/db

	echo "Fixing the LDAP files permissions and restarting slapd"
	chown -R openldap:openldap /etc/ldap/slapd.d
	chown -R openldap:openldap /var/lib/ldap
	service slapd start
}


install_re2o_server() {
echo "Re2o setup !
This tool will help you setup re2o. It is highly recommended to use a Debian clean server for this operation.
Installing sudo and dialog packages..."

export DEBIAN_FRONTEND=noninteractive

apt-get -y install sudo dialog

HEIGHT=15
WIDTH=40
CHOICE_HEIGHT=4

TITLE="Re2o setup !"
MSGBOX="This tool will help you setup re2o. It is highly recommended to use a Debian clean server for this operation."
init=$(dialog --clear \
        --title "$TITLE" \
        --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH \
        2>&1 >/dev/tty)







BACKTITLE="Re2o preconfiguration of the database"
TITLE="Database engine"
MENU="Which engine should be used as the database ?"
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





TITLE="Local extension"
INPUTBOX="The local extension to use (e.g. 'example.net'). This is used in the LDAP configuration."
extension_locale=$(dialog --title "$TITLE" \
                    --backtitle "$BACKTITLE" \
                    --inputbox "$INPUTBOX" \
                    $HEIGHT $WIDTH \
                    2>&1 >/dev/tty)
clear

IFS='.' read -a extension_locale_array <<< $extension_locale


for i in "${extension_locale_array[@]}"
do
    ldap_dn+="dc=$i,"
done
ldap_dn=${ldap_dn::-1}
echo $ldap_dn





TITLE="SQL location"
MENU="Where to install the SQL database ?
* 'Local' will setup everything automatically but is not recommended for production
* 'Remote' will ask you to manually perform some setup commands on the remote server)"
OPTIONS=(1 "Local"
         2 "Remote")
sql_is_local=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear

TITLE="SQL password"
INPUTBOX="The password to access the SQL database"
sql_password=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear


if [ $sql_is_local == 2 ]
then
    TITLE="SQL username"
    INPUTBOX="The username to access the remote SQL database"
    sql_login=$(dialog --title "$TITLE" \
    	--backtitle "$BACKTITLE" \
            --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
            2>&1 >/dev/tty)
    clear
    TITLE="SQL database name"
    INPUTBOX="The name of the remote SQL database"
    sql_name=$(dialog --title "$TITLE" \
    	--backtitle "$BACKTITLE" \
            --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
            2>&1 >/dev/tty)
    clear
    TITLE="SQL host"
    INPUTBOX="The host of the remote SQL database"
    sql_host=$(dialog --title "$TITLE" \
    	--backtitle "$BACKTITLE" \
            --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
            2>&1 >/dev/tty)
    clear
else
    sql_name="re2o"
    sql_login="re2o"
    sql_host="localhost"
fi






BACKTITLE="Re2o preconfiguration of the active directory"

TITLE="LDAP location"
MENU="Where to install the LDAP ?
* 'Local' will setup everything automatically but is not recommended for production
* 'Remote' will ask you to manually perform some setup commands on the remote server)"
OPTIONS=(1 "Local"
         2 "Remote")
ldap_is_local=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

TITLE="LDAP password"
INPUTBOX="The password to access the LDAP"
ldap_password=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear
if [ $ldap_is_local == 2 ]
then
    TITLE="CN of amdin user"
    INPUTBOX="The CN entry for the admin user of the remote LDAP"
    ldap_cn=$(dialog --title "$TITLE" \
               --backtitle "$BACKTITLE" \
               --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
               2>&1 >/dev/tty)
    clear
    TITLE="LDAP host"
    INPUTBOX="The host of the remote LDAP"
    ldap_host=$(dialog --title "$TITLE" \
                 --backtitle "$BACKTITLE" \
                 --inputbox "$INPUTBOX" $HEIGHT $WIDTH \
                 2>&1 >/dev/tty)
    clear
    TITLE="Activate TLS for remote LDAP ?"
    OPTIONS=(1 "Yes"
             2 "No")
    ldap_tls=$(dialog --title "$TITLE" \
                --backtitle "$BACKTITLE" \
                --MENU "$MENU"\
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)
    clear
else
    ldap_cn="cn=admin,"
    ldap_cn+=$ldap_dn
    ldap_host="localhost"
    ldap_tls=2
fi





BACKTITLE="Re2o preconfiguration of the mail server"

TITLE="Mail server host"
INPUTBOX="The host of the mail server to use"
email_host=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$TITLE" \
        $HEIGHT $WIDTH \
        2>&1 >/dev/tty)

TITLE="Mail server Port"
MENU="Which port (thus which protocol) to use to contact the mail server"
OPTIONS=(25 "SMTP"
         465 "SMTPS"
	 587 "Submission")
email_port=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)
clear




TITLE="Re2o setup !"
MSGBOX="Setup of the required packages"
install_base=$(dialog --clear \
	--title "$TITLE" \
        --msgbox "$MSGBOX" \
	$HEIGHT $WIDTH \
	2>&1 >/dev/tty)

echo "Setup of the required packages"
apt-get -y install python3-django python3-dateutil texlive-latex-base texlive-fonts-recommended python3-djangorestframework python3-django-reversion python3-pip libsasl2-dev libldap2-dev libssl-dev python3-crypto python3-git libjs-jquery libjs-jquery-uil libjs-jquery-timepicker libjs-bootstrap
pip3 install django-bootstrap3 django-ldapdb==0.9.0 django-macaddress





echo "SQL Database setup"
if [ $sql_bdd_type == 1 ]
then
    apt-get -y install python3-mysqldb mysql-client
    mysql_command="CREATE DATABASE $sql_name collate='utf8_general_ci';
        CREATE USER '$sql_login'@'localhost' IDENTIFIED BY '$sql_password';
        GRANT ALL PRIVILEGES ON $sql_name.* TO '$sql_login'@'localhost';
        FLUSH PRIVILEGES;"
    if [ $sql_is_local == 1 ]
    then
        apt-get -y install mysql-server
        mysql -u root --execute="$mysql_command"
    else
        echo "Please execute the following command on the remote SQL server and then continue"
        echo "$mysql_command"
        while true
	do
            read -p "Continue (y/n)?" choice
            case "$choice" in
                y|Y ) break;;
                n|N ) exit;;
                * ) echo "Invalid";;
            esac
        done
    fi
else
    apt-get -y install postgresql-client python3-psycopg2
    pgsql_command1="CREATE DATABASE $sql_name ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';"
    pgsql_command2="CREATE USER $sql_login with password '$sql_password';"
    pgsql_command3="ALTER DATABASE $sql_name owner to $sql_login;"
    if [ $sql_is_local == 1 ]
    then
        apt-get -y install postgresql
        sudo -u postgres psql --command="$pgsql_command1"
        sudo -u postgres psql --command="$pgsql_command2"
        sudo -u postgres psql --command="$pgsql_command3"
    else
        echo "Please execute the following commands on the remote SQL server and then continue"
        echo "sudo -u postgres psql $pgsql_command1"
        echo "sudo -u postgres psql $pgsql_command2"
        echo "sudo -u postgres psql $pgsql_command3"
        while true
	do
            read -p "Continue (y/n)?" choice
            case "$choice" in
                y|Y ) break;;
                n|N ) exit;;
                * ) echo "Invalid";;
            esac
        done
    fi
fi





echo "LDAP setup"
if [ $ldap_is_local == 1 ]
then
    setup_ldap $ldap_password $ldap_dn
else
    TITLE="LDAP server setup"
    MSGBOX="Please manually setup the remote LDAP server by launching the following commands: ./install_re2o.sh ldap $ldap_password $ldap_dn"
    ldap_setup=$(dialog --clear \
                  --title "$TITLE" \
                  --msgbox "$MSGBOX" \
                  $HEIGHT $WIDTH \
                  2>&1 >/dev/tty)
fi





echo "Writing of the settings_local.py file"

django_secret_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(50)]))")
aes_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(32)]))")

cp re2o/settings_local.example.py re2o/settings_local.py
if [ $sql_bdd_type == 1 ]
then
    sed -i 's/db_engine/django.db.backends.mysql/g' re2o/settings_local.py
else
    sed -i 's/db_engine/django.db.backends.postgresql_psycopg2/g' re2o/settings_local.py
fi
sed -i 's/SUPER_SECRET_KEY/'"$django_secret_key"'/g' re2o/settings_local.py
sed -i 's/SUPER_SECRET_DB/'"$sql_password"'/g' re2o/settings_local.py
sed -i 's/A_SECRET_AES_KEY/'"$aes_key"'/g' re2o/settings_local.py
sed -i 's/db_name_value/'"$sql_name"'/g' re2o/settings_local.py
sed -i 's/db_user_value/'"$sql_login"'/g' re2o/settings_local.py
sed -i 's/db_host_value/'"$sql_host"'/g' re2o/settings_local.py
sed -i 's/ldap_dn/'"$ldap_cn"'/g' re2o/settings_local.py
if [ $ldap_tls == 2 ]
then
    sed -i "s/'TLS': True,/# 'TLS': True,#/g" re2o/settings_local.py
fi
sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' re2o/settings_local.py
sed -i 's/ldap_host_ip/'"$ldap_host"'/g' re2o/settings_local.py
sed -i 's/dc=example,dc=org/'"$ldap_dn"'/g' re2o/settings_local.py
sed -i 's/example.org/'"$extension_locale"'/g' re2o/settings_local.py
sed -i 's/MY_EMAIL_HOST/'"$email_host"'/g' re2o/settings_local.py
sed -i 's/MY_EMAIL_PORT/'"$email_port"'/g' re2o/settings_local.py




TITLE="Django setup"
MSGBOX="Applying the Django database migrations"
migrations=$(dialog --clear \
	--title "$TITLE" \
        --msgbox "$MSGBOX" \
	$HEIGHT $WIDTH \
	2>&1 >/dev/tty)

python3 manage.py migrate






TITLE="Django setup"
MSGBOX="Collecting statics"
static=$(dialog --clear \
	--title "$TITLE" \
        --msgbox "$MSGBOX" \
	$HEIGHT $WIDTH \
	2>&1 >/dev/tty)

python3 manage.py collectstatic




BACKTITLE="Web server"

TITLE="Web server to use"
MENU="Which web server to install for accessing Re2o web frontend (automatic setup of nginx is not supported) ?"
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

TITLE="Web URL"
INPUTBOX="URL for accessing the web server (e.g. re2o.example.net). Be sure that this URL is accessible and correspond to a DNS entry if applicable."
url_server=$(dialog --title "$TITLE" \
	--backtitle "$BACKTITLE" \
        --inputbox "$INPUTBOX" \
	$HEIGHT $WIDTH \
        2>&1 >/dev/tty)
clear

TITLE="TLS on web server"
MENU="Would you like to activate the TLS (with Let'Encrypt) on the web server ?"
OPTIONS=(1 "Yes"
         2 "No")
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
    a2enmod wsgi
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
    TITLE="Web server setup"
    MSGBOX="Nginx automatic setup is not supported. Please configure it manually."
    web_server=$(dialog --clear \
                  --title "$TITLE" \
                  --msgbox "$MSGBOX" \
                  $HEIGHT $WIDTH \
                  2>&1 >/dev/tty)
fi

python3 manage.py createsuperuser





TITLE="End of the setup"
MSGBOX="You can now visit $url_server and connect with the credentials you just entered. This user hhas the superuser rights, meaning he can access and do everything."
end=$(dialog --clear \
	--title "$TITLE" \
        --msgbox "Vous pouvez à présent vous rendre sur $url_server, et vous connecter. Votre utilisateur dispose des privilèges superuser" \
	$HEIGHT $WIDTH \
	2>&1 >/dev/tty)
}


main_function() {
    if [ ! -z "$1" ]
    then
        if [ $1 == ldap ]
        then
            if [ ! -z "$2" ]
            then
                echo "Installation du ldap"
                setup_ldap $2 $3
            else
                echo "Arguments invalides !"
                exit
            fi
        fi
    else
        install_re2o_server
    fi
}

main_function $1 $2 $3
