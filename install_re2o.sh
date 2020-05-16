#!/bin/bash

SETTINGS_LOCAL_FILE='re2o/settings_local.py'
SETTINGS_EXAMPLE_FILE='re2o/settings_local.example.py'

APT_REQ_FILE="apt_requirements.txt"
APT_RADIUS_REQ_FILE="apt_requirements_radius.txt"
PIP_REQ_FILE="pip_requirements.txt"

LDIF_DB_FILE="install_utils/db.ldiff"
LDIF_SCHEMA_FILE="install_utils/schema.ldiff"

FREERADIUS_CLIENTS="freeradius_utils/freeradius3/clients.conf"
FREERADIUS_AUTH="freeradius_utils/auth.py"
FREERADIUS_RADIUSD="freeradius_utils/freeradius3/radiusd.conf"
FREERADIUS_MOD_PYTHON="freeradius_utils/freeradius3/mods-enabled/python"
FREERADIUS_MOD_EAP="freeradius_utils/freeradius3/mods-enabled/eap"
FREERADIUS_SITE_DEFAULT="freeradius_utils/freeradius3/sites-enabled/default"
FREERADIUS_SITE_INNER_TUNNEL="freeradius_utils/freeradius3/sites-enabled/inner-tunnel"
EDITOR="nano"

VALUE= # global value used to return values by some functions

_ask_value() {
    ### Usage _ask_value <text> [<option1> [<option2> ... ] ]
    #
    #   This function is a utility function to force a user to enter a value
    #   available in a set of options.
    #
    #   Parameters:
    #     * text: The text to display
    #     * option#: A possible option for the user. If no option is specifed,
    #       all inputs are considered valid
    #
    #   Echo: The value entered by the user. Should be one of the choices if
    #     not ommited
    ###

    shopt -s extglob

    input_text="$1"
    shift
    if [ "$#" -ne 0 ]; then
        choices="("
        while [ "$#" -ne 1 ]; do
            choices+="$1|"
            shift
        done
        choices+="$1)"
        input_text+=" $choices: "
        choices="@$choices"
    else
        input_text+=": "
        choices="@(*)"
    fi

    while true; do
        read -p "$input_text" choice
        case "$choice" in
            $choices ) break;;
            * ) echo "Invalid option";;
        esac
    done

    VALUE="$choice"
}



install_requirements() {
    ### Usage: install_requirements
    #
    #   This function will install the required packages from APT repository
    #   and Pypi repository. Those packages are all required for Re2o to work
    #   properly.
    ###

    echo "Setting up the required packages ..."
    cat $APT_REQ_FILE | xargs apt-get -y install
    pip3 install -r $PIP_REQ_FILE
    echo "Setting up the required packages: Done"
}


install_radius_requirements() {
    ### Usage: install_radius_requirements
    #
    #   This function will install the required packages from APT repository
    #   and Pypi repository. Those packages are all required for Re2o to work
    #   properly.
    ###

    echo "Setting up the required packages ..."
    cat $APT_RADIUS_REQ_FILE | xargs apt-get -y install
    python -m pip install -r $PIP_REQ_FILE
    echo "Setting up the required packages: Done"
}


configure_radius() {
    ### Usage: configure_radius
    #
    #   This function configures freeradius.
    ###
    echo "Configuring Freeradius ..."

    cat $FREERADIUS_CLIENTS >> /etc/freeradius/3.0/clients.conf
    ln -fs $(pwd)/$FREERADIUS_AUTH /etc/freeradius/3.0/auth.py
    ln -fs $(pwd)/$FREERADIUS_RADIUSD /etc/freeradius/3.0/radiusd.conf
    ln -fs $(pwd)/$FREERADIUS_MOD_PYTHON /etc/freeradius/3.0/mods-enabled/python
    ln -fs $(pwd)/$FREERADIUS_MOD_EAP /etc/freeradius/3.0/mods-enabled/eap
    ln -fs $(pwd)/$FREERADIUS_SITE_DEFAULT /etc/freeradius/3.0/sites-enabled/default
    ln -fs $(pwd)/$FREERADIUS_SITE_INNER_TUNNEL /etc/freeradius/3.0/sites-enabled/inner-tunnel
    _ask_value "Ready to edit clients.conf ?" "yes"
    $EDITOR /etc/freeradius/3.0/clients.conf


    echo "Configuring Freeradius: Done"

}



install_database() {
    ### Usage: install_database <engine_type> <local_setup> <db_name> <username> <password>
    #
    #   This function will install the database by downloading the correct APT packages
    #   and initiating the database schema.
    #
    #   Parameters:
    #     * engine_type: The DB engine to use.
    #       1 = mysql
    #       2 = postgresql
    #     * local_setup: Should the database be installed locally
    #       1 = yes
    #       2 = no
    #     * db_name: The name of the database itself
    #     * username: The username to access the database
    #     * password: The password of the user to access the database
    ###

    echo "Setting up the database ..."

    engine_type="$1"
    local_setup="$2"
    db_name="$3"
    username="$4"
    password="$5"

    if [ "$engine_type" == 1 ]; then

        echo "Installing MySQL client ..."
        apt-get -y install python3-mysqldb default-mysql-client
        echo "Installing MySQL client: Done"

        mysql_command="CREATE DATABASE $db_name collate='utf8_general_ci';
            CREATE USER '$username'@'localhost' IDENTIFIED BY '$password';
            GRANT ALL PRIVILEGES ON $db_name.* TO '$username'@'localhost';
            FLUSH PRIVILEGES;SET GLOBAL SQL_MODE=ANSI_QUOTES;"

        if [ "$local_setup" == 1 ]; then
            echo "Setting up local MySQL server ..."
            apt-get -y install default-mysql-server
            mysql -u root --execute="$mysql_command"
            echo "Setting up local MySQL server: Done"
        else
            echo "Please execute the following command on the remote SQL server and then continue"
            echo "$mysql_command"
            _ask_value "Continue" "yes" "no"; if [ "$VALUE" == "no" ]; then exit; fi
        fi

    else

        echo "Installing PostgreSQL client ..."
        apt-get -y install postgresql-client python3-psycopg2
        echo "Installing PostgreSQL client: Done"

        pgsql_command1="CREATE DATABASE $db_name ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';"
        pgsql_command2="CREATE USER $username with password '$password';"
        pgsql_command3="ALTER DATABASE $db_name owner to $username;"

        if [ "$local_setup" == 1 ]; then
            echo "Setting up local PostgreSQL server ..."
            apt-get -y install postgresql
            sudo -u postgres psql --command="$pgsql_command1"
            sudo -u postgres psql --command="$pgsql_command2"
            sudo -u postgres psql --command="$pgsql_command3"
            echo "Setting up local PostgreSQL server: Done"
        else
            echo "Please execute the following commands on the remote SQL server and then continue"
            echo "sudo -u postgres psql $pgsql_command1"
            echo "sudo -u postgres psql $pgsql_command2"
            echo "sudo -u postgres psql $pgsql_command3"
            _ask_value "Continue" "yes" "no"; if [ "$VALUE" == "no" ]; then exit; fi
        fi

    fi

    echo "Setting up the database: Done"
}



install_ldap() {
    ### Usage: install_ldap <local_setup> <password> <domain>
    #
    #   This function will install the LDAP
    #
    #   Parameters:
    #     * local_setup: Should the LDAP be installed locally ?
    #       1 = yes
    #       2 = no
    #     * password: the clear password for the admin user of the LDAP
    #     * domain: the domain extension to use for the LDAP structure in LDAP notation
    ###

    echo "Setting up the LDAP ..."

    local_setup="$1"
    password="$2"
    domain="$3"

    if [ "$local_setup" == 1 ]; then

        echo "Installing slapd package ..."
        apt-get -y install slapd
        echo "Installing slapd package: Done"

        echo "Hashing the LDAP password ..."
        hashed_ldap_passwd="$(slappasswd -s $password)"
        echo "Hash of the password: $hashed_ldap_passwd"

        echo "Building the LDAP config files ..."
        sed 's|dc=example,dc=net|'"$domain"'|g' $LDIF_DB_FILE | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/db
        sed 's|dc=example,dc=net|'"$domain"'|g' $LDIF_SCHEMA_FILE | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/schema
        echo "Building the LDAP config files: Done"

        echo "Stopping slapd service ..."
        service slapd stop
        echo "Stopping slapd service: Done"

        echo "Deleting exisitng LDAP configuration ..."
        rm -rf /etc/ldap/slapd.d/*
        rm -rf /var/lib/ldap/*
        echo "Deleting existing LDAP configuration: Done"

        echo "Setting up the new LDAP configuration ..."
        slapadd -n 0 -l /tmp/schema -F /etc/ldap/slapd.d/
        slapadd -n 1 -l /tmp/db
        echo "Setting up the new LDAP configuration: Done"

        echo "Fixing the LDAP files permissions ..."
        chown -R openldap:openldap /etc/ldap/slapd.d
        chown -R openldap:openldap /var/lib/ldap
        echo "Fixing the LDAP files permissions: Done"

        echo "Starting slapd service ..."
        service slapd start
        echo "Starting slapd service: Done"

    else

        echo "Please execute the following command on the remote LDAP server and then continue"
        echo "./install_re2o.sh setup-ldap $password $domain"
        _ask_value "Continue" "yes" "no"; if [ "$VALUE" == "no" ]; then exit; fi

    fi

    echo "Setting up the LDAP: Done"
}



write_settings_file() {
    ### Usage: write_settings_file <db_engine_type> <sql_hostname> <sql_db_name> <sql_username> <sql_password>
    #                              <ldap_cn> <ldap_tls> <ldap_password> <ldap_hostname> <ldap_domain>
    #                              <email_hostname> <email_port> <extension> <url>
    #
    #   This function will write a clean local settings file based on the example.
    #
    #   Parameters:
    #     * db_engine_type: The engine for the database
    #       1 = MySQL
    #       2 = PostgreSQL
    #     * sql_hostname: The hostname for contacting the database
    #     * sql_db_name: The name of the database itself
    #     * sql_username: The user to use to access the database
    #     * sql_password: The password to use to access the database
    #     * ldap_cn: The CN entry for the LDAP admin in LDAP notation
    #     * ldap_tls: Should the TLS be activated to contact the LDAP
    #       1 = yes
    #       2 = no
    #     * ldap_password: The password to use to connect to the LDAP
    #     * ldap_hostname: The hostname for contacting the LDAP
    #     * ldap_domain: The local domain for the LDAP in LDAP notation
    #     * email_hostname: The hostname for contacting the mail server
    #     * email_port: The port for contacting the mail server
    #     * extension: The extension to use
    #     * url: The main URL to use for Re2o
    ###

    echo "Writing of the settings_local.py file ..."

    db_engine_type="$1"
    sql_hostname="$2"
    sql_db_name="$3"
    sql_username="$4"
    sql_password="$5"
    ldap_cn="$6"
    ldap_tls="$7"
    ldap_password="$8"
    ldap_hostname="$9"
    ldap_domain="${10}"
    email_hostname="${11}"
    email_port="${12}"
    extension="${13}"
    url="${14}"

    cp "$SETTINGS_EXAMPLE_FILE" "$SETTINGS_LOCAL_FILE"

    django_secret_key="$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(50)]))")"
    aes_key="$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(32)]))")"

    if [ "$db_engine_type" == 1 ]; then
        sed -i 's/db_engine/django.db.backends.mysql/g' "$SETTINGS_LOCAL_FILE"
    else
        sed -i 's/db_engine/django.db.backends.postgresql_psycopg2/g' "$SETTINGS_LOCAL_FILE"
    fi
    sed -i 's/SUPER_SECRET_KEY/'"$django_secret_key"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/SUPER_SECRET_DB/'"$sql_password"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/A_SECRET_AES_KEY/'"$aes_key"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/db_name_value/'"$sql_db_name"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/db_user_value/'"$sql_username"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/db_host_value/'"$sql_hostname"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/ldap_dn/'"$ldap_cn"'/g' "$SETTINGS_LOCAL_FILE"
    if [ $ldap_tls == 2 ]; then
        sed -i "s/'TLS': True,/# 'TLS': True,/g" "$SETTINGS_LOCAL_FILE"
    fi
    sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/ldap_host_ip/'"$ldap_hostname"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/dc=example,dc=net/'"$ldap_domain"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/example.net/'"$extension"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/MY_EMAIL_HOST/'"$email_hostname"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/MY_EMAIL_PORT/'"$email_port"'/g' "$SETTINGS_LOCAL_FILE"
    sed -i 's/URL_SERVER/'"$url"'/g' "$SETTINGS_LOCAL_FILE"

    echo "Writing of the settings_local.py file: Done"
}



update_django() {
    ### Usage: update_django
    #
    #   This function will update the Django project by applying the migrations
    #   and collecting the statics
    ###

    echo "Applying Django migrations ..."
    python3 manage.py migrate
    echo "Applying Django migrations: Done"

    echo "Collecting web frontend statics ..."
    python3 manage.py collectstatic --noinput
    echo "Collecting web frontend statics: Done"

    echo "Generating locales ..."
    python3 manage.py compilemessages
    echo "Generating locales: Done"
}



copy_templates_files() {
    ### Usage: copy_templates_files
    #
    #   This will copy LaTeX templates in the media root.

    echo "Copying LaTeX templates ..."
    mkdir -p media/templates/
    cp cotisations/templates/cotisations/factures.tex media/templates/default_invoice.tex
    cp cotisations/templates/cotisations/voucher.tex media/templates/default_voucher.tex
    chown -R www-data:www-data media/templates/
    echo "Copying LaTeX templates: Done"
}



create_superuser() {
    ### Usage: create_superuser
    #
    #   This will create a user with the superuser rights for the project.

    echo "Creating a superuser ..."
    python3 manage.py createsuperuser
    echo "Creating a superuser: Done"
}



install_webserver() {
    ### Usage: install_webserver <engine_type> <tls> <url>
    #
    #   This function will install the web server by installing the correct APT packages
    #   and configure it
    #
    #   Parameters:
    #     * engine_type: The engine to use as a web server
    #       1 = Apache2
    #       2 = NginX
    #     * tls: Should the TLS (with LE) be generated and activated
    #       1 = yes
    #       2 = no
    #     * url: The url to access Re2o. This parameter is only used if TLS is activated
    #       for generating the certifcate with the right domain name
    ###

    echo "Setting up web server ..."

    engine_type="$1"
    tls="$2"
    url="$3"

    if [ "$engine_type" == 1 ]; then

        echo "Setting up Apache2 web server ..."

        apt-get -y install apache2 libapache2-mod-wsgi-py3
        a2enmod ssl
        a2enmod wsgi
        a2enconf javascript-common

        if [ "$tls" == 1 ]; then
            echo "Setting up TLS with LE for Apache2 web server ..."
            cp install_utils/apache2/re2o-tls.conf /etc/apache2/sites-available/re2o.conf
            apt-get -y install certbot
            apt-get -y install python-certbot-apache
            certbot certonly --rsa-key-size 4096 --apache -d "$url"
            sed -i 's/LE_PATH/'"$url"'/g' /etc/apache2/sites-available/re2o.conf
            echo "Setting up TLS with LE for Apache2 web server: Done"
        else
            cp install_utils/apache2/re2o.conf /etc/apache2/sites-available/re2o.conf
        fi

        rm /etc/apache2/sites-enabled/000-default.conf
        sed -i 's|URL_SERVER|'"$url"'|g' /etc/apache2/sites-available/re2o.conf
        sed -i 's|PATH|'"$(pwd)"'|g' /etc/apache2/sites-available/re2o.conf
        a2ensite re2o

        echo "Setting up Apache2 web server: Done"

        echo "Reloading Apache2 service ..."
        service apache2 reload
        echo "Reloading Apache2 service: Done"

    else

        echo "Nginx automatic setup is not supported. Please configure it manually."
        echo "Please confirm you have acknowledged this message."
        _ask_value "Acknowledged" "yes"

    fi

    echo "Setting up web server: Done"
}



interactive_guide() {
    ### Usage: interactive_guide
    #
    #   This function will guide through the automated setup of Re2o by asking
    #   the user for some informations and some installation choices. It will
    #   then proceed to setup and configuration of the required tools according
    #   to the user choices.
    ###

    echo "Re2o setup !"
    echo "This tool will help you setup re2o. It is highly recommended to use a Debian clean server for this operation."

    echo "Installing basic packages required for this script to work  ..."
    apt-get -y install sudo dialog
    echo "Installing basic packages required for this script to work: Done"

    # Common setup for the dialog prompts
    export DEBIAN_FRONTEND=noninteractive
    HEIGHT=20
    WIDTH=60
    CHOICE_HEIGHT=4



    #############
    ## Welcome ##
    #############

    BACKTITLE="Re2o setup"

    # Welcome prompt
    TITLE="Welcome"
    MSGBOX="This tool will help you setup re2o. It is highly recommended to use a Debian clean server for this operation."
    init="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    ######################
    ## Database options ##
    ######################

    BACKTITLE="Re2o setup - configuration of the database"

    # Prompt for choosing the database engine
    TITLE="Database engine"
    MENU="Which engine should be used as the database ?"
    OPTIONS=(1 "mysql"
             2 "postgresql")
    sql_bdd_type="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    # Prompt for choosing the database location
    TITLE="SQL location"
    MENU="Where to install the SQL database ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    sql_is_local="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    if [ $sql_is_local == 2 ]; then
        # Prompt to enter the remote database hostname
        TITLE="SQL hostname"
        INPUTBOX="The hostname of the remote SQL database"
        sql_host="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to enter the remote database name
        TITLE="SQL database name"
        INPUTBOX="The name of the remote SQL database"
        sql_name="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to enter the remote database username
        TITLE="SQL username"
        INPUTBOX="The username to access the remote SQL database"
        sql_login="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"
        clear
    else
        # Use of default values for local setup
        sql_name="re2o"
        sql_login="re2o"
        sql_host="localhost"
    fi

    # Prompt to enter the database password
    TITLE="SQL password"
    INPUTBOX="The password to access the SQL database"
    sql_password="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    ##################
    ## LDAP options ##
    ##################

    BACKTITLE="Re2o setup - configuration of the LDAP"

    # Prompt to choose the LDAP location
    TITLE="LDAP location"
    MENU="Where would you like to install the LDAP ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    ldap_is_local="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    # Prompt to enter the LDAP domain extension
    TITLE="Domain extension"
    INPUTBOX="The local domain extension to use (e.g. 'example.net'). This is used in the LDAP configuration."
    extension_locale="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    # Building the DN of the LDAP from the extension
    IFS='.' read -a extension_locale_array <<< $extension_locale
    for i in "${extension_locale_array[@]}"
    do
        ldap_dn+="dc=$i,"
    done
    ldap_dn="${ldap_dn::-1}"

    if [ "$ldap_is_local" == 2 ]; then
        # Prompt to enter the remote LDAP hostname
        TITLE="LDAP hostname"
        INPUTBOX="The hostname of the remote LDAP"
        ldap_host="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to choose if TLS should be activated or not for the LDAP
        TITLE="TLS on LDAP"
        MENU="Would you like to activate TLS for communicating with the remote LDAP ?"
        OPTIONS=(1 "Yes"
                 2 "No")
        ldap_tls="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --MENU "$MENU" \
            $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

        # Prompt to enter the admin's CN of the remote LDAP
        TITLE="CN of amdin user"
        INPUTBOX="The CN entry for the admin user of the remote LDAP"
        ldap_cn="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"
    else
        ldap_cn="cn=admin,"
        ldap_cn+="$ldap_dn"
        ldap_host="localhost"
        ldap_tls=2
    fi

    # Prompt to enter the LDAP password
    TITLE="LDAP password"
    INPUTBOX="The password to access the LDAP"
    ldap_password="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    #########################
    ## Mail server options ##
    #########################

    BACKTITLE="Re2o setup - configuration of the mail server"

    # Prompt to enter the hostname of the mail server
    TITLE="Mail server hostname"
    INPUTBOX="The hostname of the mail server to use"
    email_host="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$TITLE" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    # Prompt to choose the port of the mail server
    TITLE="Mail server port"
    MENU="Which port (thus which protocol) to use to contact the mail server"
    OPTIONS=(25 "SMTP"
             465 "SMTPS"
             587 "Submission")
    email_port="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"



    ########################
    ## Web server options ##
    ########################

    BACKTITLE="Re2o setup - configuration of the web server"

    # Prompt to choose the web server
    TITLE="Web server to use"
    MENU="Which web server to install for accessing Re2o web frontend (automatic setup of nginx is not supported) ?"
    OPTIONS=(1 "apache2"
             2 "nginx")
    web_serveur="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    # Prompt to enter the requested URL for the web frontend
    TITLE="Web URL"
    INPUTBOX="URL for accessing the web server (e.g. re2o.example.net). Be sure that this URL is accessible and correspond to a DNS entry (if applicable)."
    url_server="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    # Prompt to choose if the TLS should be setup or not for the web server
    TITLE="TLS on web server"
    MENU="Would you like to activate the TLS (with Let'Encrypt) on the web server ?"
    OPTIONS=(1 "Yes"
             2 "No")
    is_tls="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"



    ###############################
    ## End of configuration step ##
    ###############################

    BACKTITLE="Re2o setup"

    # Prompt to inform the config setup is over
    TITLE="End of configuration step"
    MSGBOX="The configuration step is now finished. The script will now perform the following actions:
    * Install the required packages
    * Install and setup the requested database if 'local' has been selected
    * Install and setup the ldap if 'local' has been selected
    * Write a local version of 'settings_local.py' file with the previously given informations
    * Apply the Django migrations for the project
    * Collect the statics for the web interface
    * Install and setup the requested web server
    * Install and setup a TLS certificate for the web server if requested"
    end_config="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    clear



    ################################
    ## Perform the actual actions ##
    ################################

    install_requirements

    install_database "$sql_bdd_type" "$sql_is_local" "$sql_name" "$sql_login" "$sql_password"

    install_ldap "$ldap_is_local" "$ldap_password" "$ldap_dn"


    write_settings_file "$sql_bdd_type" "$sql_host" "$sql_name" "$sql_login" "$sql_password" \
                        "$ldap_cn" "$ldap_tls" "$ldap_password" "$ldap_host" "$ldap_dn" \
                        "$email_host" "$email_port" "$extension_locale" "$url_server"

    update_django

    create_superuser

    install_webserver "$web_serveur" "$is_tls" "$url_server"

    copy_templates_files


    ###########################
    ## End of the setup step ##
    ###########################

    BACKTITLE="Re2o setup"

    # Prompt to inform the installation process is over
    TITLE="End of the setup"
    MSGBOX="You can now visit $url_server and connect with the credentials you just entered. This user has the superuser rights, meaning he can access and do everything."
    end="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"
}



interactive_radius_guide() {
    ### Usage: interactive_radius_guide
    #
    #   This function will guide through the automated setup of radius with
    #   Re2o by asking the user for some informations and some installation
    #   choices. It will then proceed to setup and configuration of the
    #   required tools according to the user choices.
    ###

    echo "Re2o setup !"
    echo "This tool will help you setup re2o radius. It is highly recommended to use a Debian clean server for this operation."

    echo "Installing basic packages required for this script to work  ..."
    apt-get -y install sudo dialog
    echo "Installing basic packages required for this script to work: Done"

    # Common setup for the dialog prompts
    export DEBIAN_FRONTEND=noninteractive
    HEIGHT=20
    WIDTH=60
    CHOICE_HEIGHT=4



    #############
    ## Welcome ##
    #############

    BACKTITLE="Re2o setup"

    # Welcome prompt
    TITLE="Welcome"
    MSGBOX="This tool will help you setup re2o. It is highly recommended to use a Debian clean server for this operation."
    init="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    ######################
    ## Database options ##
    ######################

    BACKTITLE="Re2o setup - configuration of the database"

    # Prompt for choosing the database engine
    TITLE="Database engine"
    MENU="Which engine should be used as the database ?"
    OPTIONS=(1 "mysql"
             2 "postgresql")
    sql_bdd_type="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    # Prompt for choosing the database location
    TITLE="SQL location"
    MENU="Where to install the SQL database ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    sql_is_local="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    if [ $sql_is_local == 2 ]; then
        # Prompt to enter the remote database hostname
        TITLE="SQL hostname"
        INPUTBOX="The hostname of the remote SQL database"
        sql_host="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to enter the remote database name
        TITLE="SQL database name"
        INPUTBOX="The name of the remote SQL database"
        sql_name="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to enter the remote database username
        TITLE="SQL username"
        INPUTBOX="The username to access the remote SQL database"
        sql_login="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"
        clear
    else
        # Use of default values for local setup
        sql_name="re2o"
        sql_login="re2o"
        sql_host="localhost"
    fi

    # Prompt to enter the database password
    TITLE="SQL password"
    INPUTBOX="The password to access the SQL database"
    sql_password="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    ##################
    ## LDAP options ##
    ##################

    BACKTITLE="Re2o setup - configuration of the LDAP"

    # Prompt to choose the LDAP location
    TITLE="LDAP location"
    MENU="Where would you like to install the LDAP ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    ldap_is_local="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

    # Prompt to enter the LDAP domain extension
    TITLE="Domain extension"
    INPUTBOX="The local domain extension to use (e.g. 'example.net'). This is used in the LDAP configuration."
    extension_locale="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    # Building the DN of the LDAP from the extension
    IFS='.' read -a extension_locale_array <<< $extension_locale
    for i in "${extension_locale_array[@]}"
    do
        ldap_dn+="dc=$i,"
    done
    ldap_dn="${ldap_dn::-1}"

    if [ "$ldap_is_local" == 2 ]; then
        # Prompt to enter the remote LDAP hostname
        TITLE="LDAP hostname"
        INPUTBOX="The hostname of the remote LDAP"
        ldap_host="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"

        # Prompt to choose if TLS should be activated or not for the LDAP
        TITLE="TLS on LDAP"
        MENU="Would you like to activate TLS for communicating with the remote LDAP ?"
        OPTIONS=(1 "Yes"
                 2 "No")
        ldap_tls="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --MENU "$MENU" \
            $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"

        # Prompt to enter the admin's CN of the remote LDAP
        TITLE="CN of amdin user"
        INPUTBOX="The CN entry for the admin user of the remote LDAP"
        ldap_cn="$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)"
    else
        ldap_cn="cn=admin,"
        ldap_cn+="$ldap_dn"
        ldap_host="localhost"
        ldap_tls=2
    fi

    # Prompt to enter the LDAP password
    TITLE="LDAP password"
    INPUTBOX="The password to access the LDAP"
    ldap_password="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"



    #########################
    ## Mail server options ##
    #########################

    BACKTITLE="Re2o setup - configuration of the mail server"

    # Prompt to enter the hostname of the mail server
    TITLE="Mail server hostname"
    INPUTBOX="The hostname of the mail server to use"
    email_host="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$TITLE" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    # Prompt to choose the port of the mail server
    TITLE="Mail server port"
    MENU="Which port (thus which protocol) to use to contact the mail server"
    OPTIONS=(25 "SMTP"
             465 "SMTPS"
             587 "Submission")
    email_port="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)"



    ###############################
    ## End of configuration step ##
    ###############################

    BACKTITLE="Re2o setup"

    # Prompt to inform the config setup is over
    TITLE="End of configuration step"
    MSGBOX="The configuration step is now finished. The script will now perform the following actions:
    * Install the required packages
    * Install and setup the requested database if 'local' has been selected
    * Install and setup the ldap if 'local' has been selected
    * Write a local version of 'settings_local.py' file with the previously given informations
    * Apply the Django migrations for the project
    * Install and setup freeradius"
    end_config="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"

    clear



    ################################
    ## Perform the actual actions ##
    ################################

    install_radius_requirements

    configure_radius

    install_database "$sql_bdd_type" "$sql_is_local" "$sql_name" "$sql_login" "$sql_password"

    install_ldap "$ldap_is_local" "$ldap_password" "$ldap_dn"


    write_settings_file "$sql_bdd_type" "$sql_host" "$sql_name" "$sql_login" "$sql_password" \
                        "$ldap_cn" "$ldap_tls" "$ldap_password" "$ldap_host" "$ldap_dn" \
                        "$email_host" "$email_port" "$extension_locale" "$url_server"

    update_django


    ###########################
    ## End of the setup step ##
    ###########################

    BACKTITLE="Re2o setup"

    # Prompt to inform the installation process is over
    TITLE="End of the setup"
    MSGBOX="You can now use your RADIUS server."
    end="$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)"
}





interactive_update_settings() {
    ### Usage: interactvie_update_settings
    #
    #   This function will take the parameters in the example settings file, retrieve the
    #   existing parameters from the local settings file and ask the user for the missing parameters
    ###
    _ask_value "Database engine" "mysql" "postgresql"; if [ "$VALUE" == "mysql" ]; then db_engine_type=1; else db_engine_type=2; fi
    _ask_value "Database hostname"; sql_hostname="$VALUE"
    _ask_value "Database name"; sql_db_name="$VALUE"
    _ask_value "Database username"; sql_username="$VALUE"
    _ask_value "Database password"; sql_password="$VALUE"
    _ask_value "LDAP hostname"; ldap_hostname="$VALUE"
    _ask_value "Activate TLS on LDAP" "yes" "no"; if [ "$VALUE" == "mysql" ]; then ldap_tls=1; else ldap_tls=2; fi
    _ask_value "LDAP domain (e.g. 'dc=example,dc=net')"; ldap_domain="$VALUE"
    _ask_value "LDAP admin CN entry (e.g. 'cn=admin,dc=example,dc=net')"; ldap_cn="$VALUE"
    _ask_value "LDAP password"; ldap_password="$VALUE"
    _ask_value "Mail server hostname"; email_hostname="$VALUE"
    _ask_value "Mail server port" "25" "465" "587"; email_port="$VALUE"
    _ask_value "Extension de domain (e.g. 'example.net')"; extension="$VALUE"
    _ask_value "Main URL"; url="$VALUE"
    write_settings_file "$db_engine_type" "$sql_hostname" "$sql_db_name" "$sql_username" "$sql_password" \
                        "$ldap_cn" "$ldap_tls" "$ldap_password" "$ldap_hostname" "$ldap_domain" \
                        "$email_hostname" "$email_port" "$extension" "$url"

}



main_function() {
    ### Usage: main_function [subcommand [options]]
    #
    #   This function will parse the arguments to determine which part of the tool to start.
    #   Refer to the help message below for the details of the parameters
    ###

    if [ -z "$1" ] || [ "$1" == "help" ]; then
        echo ""
        echo "Usage: install_re2o [subcommand [options]]"
        echo ""
        echo "The 'install_re2o' script is a utility script to setup, configure, reset and update"
        echo "some components of re2o. Please refer to the following details for more."
        echo ""
        echo "Sub-commands:"
        echo "  * [no subcommand] - Display this quick usage documentation"
        echo "  * {help} ---------- Display this quick usage documentation"
        echo "  * {setup} --------- Launch the full interactive guide to setup entirely"
        echo "                      re2o from scratch"
        echo "  * {setup-radius} -- Launch the full interactive guide to setup entirely"
        echo "                      re2o radius from scratch"
        echo "  * {update} -------- Collect frontend statics, install the missing APT"
        echo "                      and pip packages, copy LaTeX templates files"
	echo "                      and apply the migrations to the DB"
        echo "  * {update-radius} - Update radius apt and pip packages and copy radius"
        echo "                      configuration files to their proper location."
        echo "  * {update-django} - Apply Django migration and collect frontend statics"
        echo "  * {copy-template-files} - Copy LaTeX templates files to media/templates"
        echo "  * {update-packages} Install the missing APT and pip packages"
        echo "  * {update-settings} Interactively rewrite the settings file"
        echo "  * {reset-db} ------ Erase the previous local database, setup a new empty"
        echo "                      one and apply the Django migrations on it and collect"
        echo "                      Django statics."
        echo "      Parameters:"
        echo "        * <db_password> -- the clear-text password to connect to the database"
        echo "        * [db_engine_type] the SQL engine to use ('mysql' or 'postgresql')."
        echo "                           Default is 'mysql'."
        echo "        * [db_name] ------ the name of the database itself."
        echo "                           Default is 're2o'."
        echo "        * [db_username] -- the username to connect to the database."
        echo "                           Default is 're2o'."
        echo "  * {reset-ldap} ---- Erase the previous local LDAP and setup a new empty one"
        echo "      Parameters:"
        echo "        * <ldap_password> the clear-text password for the admin user of the"
        echo "                          LDAP"
        echo "        * <local_domain>  the domain extension to use for the LDAP structure"
        echo "                          in LDAP notation"
        echo ""
    else
        subcmd="$1"

        case "$subcmd" in

        setup )
           interactive_guide
           ;;

        setup-radius )
            interactive_radius_guide
            ;;

        update )
            install_requirements
            copy_templates_files
            update_django
            ;;

        update-radius )
            install_radius_requirements
            configure_radius
            ;;

        copy-templates-files )
            copy_templates_files
            ;;

        update-django )
            update_django
            ;;

        update-packages )
            install_requirements
            ;;

        update-settings )
            interactive_update_settings
            ;;

        reset-db )
            if [ ! -z "$2" ]; then
                db_password="$2"
                case "$3" in
                mysql )
                    db_engine_type=1;;
                postresql )
                    db_engine_type=2;;
                * )
                    db_engine_type=1;;
                esac
                if [ ! -z "$4" ]; then
                    db_name="$4"
                else
                    db_name="re2o"
                fi
                if [ ! -z "$5" ]; then
                    db_username="$5"
                else
                    db_username="re2o"
                fi
                install_database "$db_engine_type" 1 "$db_name" "$db_username" "$db_password"
		update_django
            else
                echo "Invalid arguments !"
                echo "Usage: install_re2o setup-db <db_password> [<db_engine_type>] [<db_name>] [<db_username>]"
		echo "See 'install_re2o help' for further help"
            fi
            ;;

        reset-ldap )
            if [ ! -z "$2" ] && [ ! -z "$3" ]; then
                ldap_password="$2"
                local_domain="$3"
                install_ldap 1 "$ldap_password" "$local_domain"
            else
                echo "Invalid arguments !"
                echo "Usage: install_re2o setup-ldap <ldap_password> <local_domain>"
		echo "See 'install_re2o help' for further help"
            fi
            ;;

        * )
            echo "Unknown subcommand: $subcmd"
            echo "Use 'install_re2o help' to display some help"
            ;;

        esac
    fi
}

main_function "$@"
