#!/bin/bash

setup_ldap() {
    ### Usage: setup_ldap <ldap_password> <local_domain>
    #
    #   This function is used to setup the LDAP structure based on the ldiff files
    #   located in 'install_utils/'. It will delete the previous structure and data
    #   and recreate a new empty one.
    #   
    #   Parameters:
    #     * ldap_password: the clear password for the admin user of the LDAP
    #     * local_domain: the domain extension to use for the LDAP structure in LDAP notation
    ###

    apt-get -y install slapd

    echo "Hashing the LDAP password ..."
    hashed_ldap_passwd=$(slappasswd -s $1)
    echo "Hash of the password: $hashed_ldap_passwd"

    echo "Building the LDAP config files ..."
    sed 's|dc=example,dc=org|'"$2"'|g' install_utils/db.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/db
    sed 's|dc=example,dc=org|'"$2"'|g' install_utils/schema.ldiff | sed 's|FILL_IT|'"$hashed_ldap_passwd"'|g' > /tmp/schema
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
}


install_re2o_server() {
    ### Usage: install_re2o_server
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
    init=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)



    ######################
    ## Database options ##
    ######################

    BACKTITLE="Re2o setup - configuration of the database"

    # Prompt for choosing the database engine
    TITLE="Database engine"
    MENU="Which engine should be used as the database ?"
    OPTIONS=(1 "mysql"
             2 "postgresql")
    sql_bdd_type=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)

    # Prompt for choosing the database location
    TITLE="SQL location"
    MENU="Where to install the SQL database ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    sql_is_local=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)

    if [ $sql_is_local == 2 ]; then
        # Prompt to enter the remote database hostname
        TITLE="SQL hostname"
        INPUTBOX="The hostname of the remote SQL database"
        sql_host=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)
        
        # Prompt to enter the remote database name
        TITLE="SQL database name"
        INPUTBOX="The name of the remote SQL database"
        sql_name=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)

        # Prompt to enter the remote database username
        TITLE="SQL username"
        INPUTBOX="The username to access the remote SQL database"
        sql_login=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)
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
    sql_password=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)



    ##############################
    ## Active directory options ##
    ##############################

    BACKTITLE="Re2o setup - configuration of the active directory"

    # Prompt to choose the LDAP location
    TITLE="LDAP location"
    MENU="Where would you like to install the LDAP ?
    * 'Local' will setup everything automatically but is not recommended for production
    * 'Remote' will ask you to manually perform some setup commands on the remote server"
    OPTIONS=(1 "Local"
             2 "Remote")
    ldap_is_local=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)
    
    # Prompt to enter the LDAP domain extension
    TITLE="Domain extension"
    INPUTBOX="The local domain extension to use (e.g. 'example.net'). This is used in the LDAP configuration."
    extension_locale=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)
    
    # Building the DN of the LDAP from the extension
    IFS='.' read -a extension_locale_array <<< $extension_locale
    for i in "${extension_locale_array[@]}"
    do
        ldap_dn+="dc=$i,"
    done
    ldap_dn=${ldap_dn::-1}

    if [ $ldap_is_local == 2 ]; then
        # Prompt to enter the remote LDAP hostname
        TITLE="LDAP hostname"
        INPUTBOX="The hostname of the remote LDAP"
        ldap_host=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)
        
        # Prompt to choose if TLS should be activated or not for the LDAP
        TITLE="TLS on LDAP"
        MENU="Would you like to activate TLS for communicating with the remote LDAP ?"
        OPTIONS=(1 "Yes"
                 2 "No")
        ldap_tls=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --MENU "$MENU" \
            $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)

        # Prompt to enter the admin's CN of the remote LDAP
        TITLE="CN of amdin user"
        INPUTBOX="The CN entry for the admin user of the remote LDAP"
        ldap_cn=$(dialog --clear --backtitle "$BACKTITLE" \
            --title "$TITLE" --inputbox "$INPUTBOX" \
            $HEIGHT $WIDTH 2>&1 >/dev/tty)
    else
        ldap_cn="cn=admin,"
        ldap_cn+=$ldap_dn
        ldap_host="localhost"
        ldap_tls=2
    fi

    # Prompt to enter the LDAP password
    TITLE="LDAP password"
    INPUTBOX="The password to access the LDAP"
    ldap_password=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)



    #########################
    ## Mail server options ##
    #########################

    BACKTITLE="Re2o setup - configuration of the mail server"
    
    # Prompt to enter the hostname of the mail server
    TITLE="Mail server hostname"
    INPUTBOX="The hostname of the mail server to use"
    email_host=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$TITLE" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)

    # Prompt to choose the port of the mail server    
    TITLE="Mail server port"
    MENU="Which port (thus which protocol) to use to contact the mail server"
    OPTIONS=(25 "SMTP"
             465 "SMTPS"
             587 "Submission")
    email_port=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)



    ########################
    ## Web server options ##
    ########################

    BACKTITLE="Re2o setup - configuration of the web server"
    
    # Prompt to choose the web server
    TITLE="Web server to use"
    MENU="Which web server to install for accessing Re2o web frontend (automatic setup of nginx is not supported) ?"
    OPTIONS=(1 "apache2"
             2 "nginx")
    web_serveur=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)
    
    # Prompt to enter the requested URL for the web frontend
    TITLE="Web URL"
    INPUTBOX="URL for accessing the web server (e.g. re2o.example.net). Be sure that this URL is accessible and correspond to a DNS entry (if applicable)."
    url_server=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --inputbox "$INPUTBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)
    
    # Prompt to choose if the TLS should be setup or not for the web server
    TITLE="TLS on web server"
    MENU="Would you like to activate the TLS (with Let'Encrypt) on the web server ?"
    OPTIONS=(1 "Yes"
             2 "No")
    is_tls=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --menu "$MENU" \
        $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)



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
    end_config=$(dialog --clear --backtitle "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)

    clear


    ###############################
    ## Install required packages ##
    ###############################

    echo "Setting up the required packages ..."
    apt-get -y install \
        python3-django \
        python3-dateutil \
        texlive-latex-base \
        texlive-fonts-recommended \
        python3-djangorestframework \
        python3-django-reversion \
        python3-pip \
        libsasl2-dev libldap2-dev \
        libssl-dev \
        python3-crypto \
        python3-git \
        javascript-common \
        libjs-jquery \
        libjs-jquery-ui \
        libjs-jquery-timepicker \
        libjs-bootstrap
    pip3 install django-bootstrap3 django-ldapdb==0.9.0 django-macaddress
    echo "Setting up the required packages: Done"



    ####################
    ## Setup database ##
    ####################

    echo "Setting up the database ..."

    if [ $sql_bdd_type == 1 ]; then

        echo "Installing MySQL client ..."
        apt-get -y install python3-mysqldb mysql-client
        echo "Installing MySQL client: Done"

        mysql_command="CREATE DATABASE $sql_name collate='utf8_general_ci';
            CREATE USER '$sql_login'@'localhost' IDENTIFIED BY '$sql_password';
            GRANT ALL PRIVILEGES ON $sql_name.* TO '$sql_login'@'localhost';
            FLUSH PRIVILEGES;"

        if [ $sql_is_local == 1 ]; then
            echo "Setting up local MySQL server ..."
            apt-get -y install mysql-server
            mysql -u root --execute="$mysql_command"
            echo "Setting up local MySQL server: Done"
        else
            echo "Please execute the following command on the remote SQL server and then continue"
            echo "$mysql_command"
            while true; do
                read -p "Continue (y/n)?" choice
                case "$choice" in
                    y|Y ) break;;
                    n|N ) exit;;
                    * ) echo "Invalid";;
                esac
            done
        fi

    else

        echo "Installing PostgreSQL client ..."
        apt-get -y install postgresql-client python3-psycopg2
        echo "Installing PostgreSQL client: Done"

        pgsql_command1="CREATE DATABASE $sql_name ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';"
        pgsql_command2="CREATE USER $sql_login with password '$sql_password';"
        pgsql_command3="ALTER DATABASE $sql_name owner to $sql_login;"

        if [ $sql_is_local == 1 ]; then
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
            while true; do
                read -p "Continue (y/n)?" choice
                case "$choice" in
                    y|Y ) break;;
                    n|N ) exit;;
                    * ) echo "Invalid";;
                esac
            done
        fi

    fi

    echo "Setting up the database: Done"



    ############################
    ## Setup active directory ##
    ############################

    echo "Setting up the active direcory ..."

    if [ $ldap_is_local == 1 ]; then

        echo "Setting up local active directory ..."
        setup_ldap $ldap_password $ldap_dn
        echo "Setting up local active directory: Done"

    else

        echo "Please execute the following command on the remote LDAP server and then continue"
        echo "./install_re2o.sh ldap $ldap_password $ldap_dn"
        while true; do
            read -p "Continue (y/n)?" choice
            case "$choice" in
                y|Y ) break;;
                n|N ) exit;;
                * ) echo "Invalid";;
            esac
        done

    fi

    echo "Setting up the active directory: Done"



    ###################################
    ## Setup settings_locale.py file ##
    ###################################

    echo "Writing of the settings_local.py file ..."

    django_secret_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(50)]))")
    aes_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(32)]))")
    
    cp re2o/settings_local.example.py re2o/settings_local.py

    if [ $sql_bdd_type == 1 ]; then
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
    if [ $ldap_tls == 2 ]; then
        sed -i "s/'TLS': True,/# 'TLS': True,#/g" re2o/settings_local.py
    fi
    sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' re2o/settings_local.py
    sed -i 's/ldap_host_ip/'"$ldap_host"'/g' re2o/settings_local.py
    sed -i 's/dc=example,dc=org/'"$ldap_dn"'/g' re2o/settings_local.py
    sed -i 's/example.org/'"$extension_locale"'/g' re2o/settings_local.py
    sed -i 's/MY_EMAIL_HOST/'"$email_host"'/g' re2o/settings_local.py
    sed -i 's/MY_EMAIL_PORT/'"$email_port"'/g' re2o/settings_local.py
    sed -i 's/URL_SERVER/'"$url_server"'/g' re2o/settings_local.py

    echo "Writing of the settings_local.py file: Done"



    #############################
    ## Apply Django migrations ##
    #############################

    echo "Applying Django migrations ..."
    python3 manage.py migrate
    echo "Applying Django migrations: Done"



    ######################
    ## Create superuser ##
    ######################

    echo "Creating a superuser ..."
    python3 manage.py createsuperuser
    echo "Creating a superuser: Done"



    ##################################
    ## Collect web frontend statics ##
    ##################################

    echo "Collecting web frontend statics ..."
    python3 manage.py collectstatic
    echo "Collecting web frontend statics: Done"



    #######################
    ## Set up web server ##
    #######################

    echo "Setting up web server ..."

    if [ $web_serveur == 1 ]; then

        echo "Setting up Apache2 web server ..."

        apt-get -y install apache2 libapache2-mod-wsgi-py3
        a2enmod ssl
        a2enmod wsgi
        a2enconf javascript-common

        if [ $is_tls == 1 ]; then
            echo "Setting up TLS with LE for Apache2 web server ..."
            cp install_utils/apache2/re2o-tls.conf /etc/apache2/sites-available/re2o.conf
            apt-get -y install certbot
            apt-get -y install python-certbot-apache
            certbot certonly --rsa-key-size 4096 --apache -d $url_server
            sed -i 's/LE_PATH/'"$url_server"'/g' /etc/apache2/sites-available/re2o.conf
            echo "Setting up TLS with LE for Apache2 web server: Done"
        else
            cp install_utils/apache2/re2o.conf /etc/apache2/sites-available/re2o.conf
        fi

        rm /etc/apache2/sites-enabled/000-default.conf
        sed -i 's|URL_SERVER|'"$url_server"'|g' /etc/apache2/sites-available/re2o.conf
        current_path=$(pwd)
        sed -i 's|PATH|'"$current_path"'|g' /etc/apache2/sites-available/re2o.conf
        a2ensite re2o

        echo "Setting up Apache2 web server: Done"

        echo "Reloading Apache2 service ..."
        service apache2 reload
        echo "Reloading Apache2 service: Done"

    else

        echo "Nginx automatic setup is not supported. Please configure it manually."
        echo "Please onfirm you have acknowledged this message."
        while true; do
            read -p "Acknowledged (y/n)?" choice
            case "$choice" in
                y|Y ) break;;
                n|N ) exit;;
                * ) echo "Invalid";;
            esac
        done

    fi

    echo "Setting up web server: Done"



    ###########################
    ## End of the setup step ##
    ###########################

    BACKTITLE="Re2o setup"

    # Prompt to inform the installation process is over
    TITLE="End of the setup"
    MSGBOX="You can now visit $url_server and connect with the credentials you just entered. This user hhas the superuser rights, meaning he can access and do everything."
    end=$(dialog --clear --BACKTITLE "$BACKTITLE" \
        --title "$TITLE" --msgbox "$MSGBOX" \
        $HEIGHT $WIDTH 2>&1 >/dev/tty)
}


main_function() {
    ### Usage: main_function [ldap <ldap_password> [<local_domain>]]
    #
    #   This function will parse the arguments to determine which part of the tool to start.
    #   If launched with no arguments, the full setup guide will be started.
    #   If launched with the 'ldap' argument, only the ldap setup will performed.
    #
    #   Parameters:
    #     * ldap_password: the clear password for the admin user of the LDAP
    #     * local_domain: the domain extension to use for the LDAP structure in LDAP notation
    ###

    if [ ! -z "$1" ]; then
        if [ $1 == ldap ]; then
            if [ ! -z "$2" ]; then
                echo "Setting up local active directory ..."
                setup_ldap $2 $3
                echo "Setting up local active directory: Done"
            else
                echo "Arguments invalides !"
                echo "Usage: ./install_re2o.sh [ldap <ldap_password> [<local_domain>]]"
                exit
            fi
        fi
    else
        install_re2o_server
    fi
}

main_function $1 $2 $3
