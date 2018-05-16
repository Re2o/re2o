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


install_requirements() {
    ### Usage: install_requirements 
    #
    #   This function will install the required packages from APT repository
    #   and Pypi repository. Those packages are qll required for Re2o to work
    #   properly.
    ###

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

    engine_type=$1
    local_setup=$2
    db_name=$3
    username=$4
    password=$5

    if [ $engine_type == 1 ]; then

        echo "Installing MySQL client ..."
        apt-get -y install python3-mysqldb mysql-client
        echo "Installing MySQL client: Done"

        mysql_command="CREATE DATABASE $db_name collate='utf8_general_ci';
            CREATE USER '$username'@'localhost' IDENTIFIED BY '$password';
            GRANT ALL PRIVILEGES ON $db_name.* TO '$username'@'localhost';
            FLUSH PRIVILEGES;"

        if [ $local_setup == 1 ]; then
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

        pgsql_command1="CREATE DATABASE $db_name ENCODING 'UTF8' LC_COLLATE='fr_FR.UTF-8' LC_CTYPE='fr_FR.UTF-8';"
        pgsql_command2="CREATE USER $username with password '$password';"
        pgsql_command3="ALTER DATABASE $db_name owner to $username;"

        if [ $local_setup == 1 ]; then
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
}



init_django() {
    ### Usage: init_django
    #
    #   This function will initialise the Django project by applying the migrations,
    #   creating a first user with the superuser rights and collecting the statics
    ###

    echo "Applying Django migrations ..."
    python3 manage.py migrate
    echo "Applying Django migrations: Done"

    echo "Creating a superuser ..."
    python3 manage.py createsuperuser
    echo "Creating a superuser: Done"

    echo "Collecting web frontend statics ..."
    python3 manage.py collectstatic --noinput
    echo "Collecting web frontend statics: Done"
}



install_active_directory() {
    ### Usage: install_active_directory <local_setup> <password> <domain>
    #
    #   This function will install the active directory
    #
    #   Parameters:
    #     * local_setup: Should the Active Directory be installed locally ?
    #       1 = yes
    #       2 = no
    #     * password: the clear password for the admin user of the LDAP
    #     * domain: the domain extension to use for the LDAP structure in LDAP notation
    ###

    echo "Setting up the active direcory ..."

    local_setup=$1
    password=$2
    domain=$3

    if [ $local_setup == 1 ]; then

        echo "Setting up local active directory ..."
        setup_ldap $password $domain
        echo "Setting up local active directory: Done"

    else

        echo "Please execute the following command on the remote LDAP server and then continue"
        echo "./install_re2o.sh ldap $password $domain"
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
    #     * ldap_cn: The CN entry for the Active Directory admin in LDAP notation
    #     * ldap_tls: Should the TLS be activated to contact the Active Directory
    #       1 = yes
    #       2 = no
    #     * ldap_password: The password to use to connect to the Active Directoryy
    #     * ldap_hostname: The hostname for contacting the Active Directory
    #     * ldap_domain: The local domain for the Active Directory in LDAP notation
    #     * email_hostname: The hostname for contacting the mail server
    #     * email_port: The port for contacting the mail server
    #     * extension: The extension to use
    #     * url: The main URL to use for Re2o
    ###

    echo "Writing of the settings_local.py file ..."

    db_engine_type=$1
    sql_hostname=$2
    sql_db_name=$3
    sql_username=$4
    sql_password=$5
    ldap_cn=$6
    ldap_tls=$7
    ldap_password=$8
    ldap_hostname=$9
    ldap_domain=${10}
    email_hostname=${11}
    email_port=${12}
    extension=${13}
    url=${14}

    SETTINGS_LOCAL_FILE='re2o/settings_local.py'
    SETTINGS_EXAMPLE_FILE='re2o/settings_local.example.py'

    cp $SETTINGS_EXAMPLE_FILE $SETTINGS_LOCAL_FILE

    django_secret_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(50)]))")
    aes_key=$(python -c "import random; print(''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789%=+') for i in range(32)]))")
    
    if [ $db_engine_type == 1 ]; then
        sed -i 's/db_engine/django.db.backends.mysql/g' $SETTINGS_LOCAL_FILE
    else
        sed -i 's/db_engine/django.db.backends.postgresql_psycopg2/g' $SETTINGS_LOCAL_FILE
    fi
    sed -i 's/SUPER_SECRET_KEY/'"$django_secret_key"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/SUPER_SECRET_DB/'"$sql_password"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/A_SECRET_AES_KEY/'"$aes_key"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/db_name_value/'"$sql_db_name"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/db_user_value/'"$sql_username"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/db_host_value/'"$sql_hostname"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/ldap_dn/'"$ldap_cn"'/g' $SETTINGS_LOCAL_FILE
    if [ $ldap_tls == 2 ]; then
        sed -i "s/'TLS': True,/# 'TLS': True,#/g" $SETTINGS_LOCAL_FILE
    fi
    sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/ldap_host_ip/'"$ldap_hostname"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/dc=example,dc=org/'"$ldap_domain"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/example.org/'"$extension"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/MY_EMAIL_HOST/'"$email_hostname"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/MY_EMAIL_PORT/'"$email_port"'/g' $SETTINGS_LOCAL_FILE
    sed -i 's/URL_SERVER/'"$url"'/g' $SETTINGS_LOCAL_FILE

    echo "Writing of the settings_local.py file: Done"
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

    engine_type=$1
    tls=$2
    url=$3

    if [ $engine_type == 1 ]; then

        echo "Setting up Apache2 web server ..."

        apt-get -y install apache2 libapache2-mod-wsgi-py3
        a2enmod ssl
        a2enmod wsgi
        a2enconf javascript-common

        if [ $tls == 1 ]; then
            echo "Setting up TLS with LE for Apache2 web server ..."
            cp install_utils/apache2/re2o-tls.conf /etc/apache2/sites-available/re2o.conf
            apt-get -y install certbot
            apt-get -y install python-certbot-apache
            certbot certonly --rsa-key-size 4096 --apache -d $url
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



    ################################
    ## Perform the actual actions ##
    ################################

    install_requirements

    install_database $sql_bdd_type $sql_is_local $sql_name $sql_login $sql_password

    install_active_directory $ldap_is_local $ldap_password $ldap_dn


    write_settings_file $sql_bdd_type $sql_host $sql_name $sql_login $sql_password \
                        $ldap_cn $ldap_tls $ldap_password $ldap_host $ldap_dn \
                        $email_host $email_port $extension_locale $url_server

    init_django
    
    install_webserver $web_serveur $is_tls $url_server



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
