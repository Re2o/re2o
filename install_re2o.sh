echo "Installation de Re2o ! 
Cet utilitaire va procéder à l'installation initiale de re2o. Le serveur présent doit être vierge.
Preconfiguration..."
while true; do
    read -p "Moteur de bdd choisi (mysql ou postgresql)" sql_bdd_type
    case $sql_bdd_type in
	    [mysql]* ) break;;
	    [postgresql]* ) break;;
    * ) echo "Réponse incorrecte";;
esac
done

read -p "Extension locale (ex : example.org)" extension_locale
IFS='.' read -a extension_locale_array <<< $extension_locale


for i in "${extension_locale_array[@]}"
do
    ldap_dn+="dc=$i,"
done
ldap_dn=${ldap_dn::-1}
echo $ldap_dn

while true; do
    read -p "Installer la base de donnée sql en local (Y/N)" sql_is_local
    case $sql_is_local in
	    [N]* ) echo "Vous devrez fournir un login/mdp/host dans ce cas"; break;;
	    [Y]* ) break;;
    * ) echo "Réponse incorrecte (Y/N)";;
esac
done

read -p "Mot de passe sql " sql_password
if [ $sql_is_local == "N" ]
then 
read -p "Login sql " sql_login
read -p "Nom bdd sql " sql_name
read -p "Hote de la base de donnée " sql_host 
else
sql_name="re2o"
sql_login="re2o"
sql_host="localhost"
fi

sql_command="CREATE DATABASE $sql_name collate='utf8_general_ci';
CREATE USER '$sql_login'@'localhost' IDENTIFIED BY '$sql_password';
GRANT ALL PRIVILEGES ON $sql_name.* TO '$sql_login'@'localhost';
FLUSH PRIVILEGES;"

while true; do
    read -p "Installer la base de donnée ldap en local (Y/N)" ldap_is_local
    case $ldap_is_local in
    [N]* ) echo "Vous devrez fournir un login/mdp/host dans ce cas"; break;;
    [Y]* ) break;;
    * ) echo "Réponse incorrecte (Y/N)";;
esac
done


read -p "Mot de passe ldap " ldap_password
if [ $ldap_is_local == "N" ]
then 
read -p "Cn admin à utiliser " ldap_cn
read -p "Hote de la base de donnée (adresse ip seulement !)" ldap_host 
else
ldap_cn="cn=admin,"
ldap_cn+=$ldap_dn
ldap_host="localhost"
fi


echo "Installation des paquets de base"
export DEBIAN_FRONTEND=noninteractive
apt-get -y install python3-django python3-dateutil texlive-latex-base texlive-fonts-recommended python3-djangorestframework python3-django-reversion python3-pip libsasl2-dev libldap2-dev libssl-dev
pip3 install django-bootstrap3
pip3 install django-ldapdb
pip3 install django-macaddress

if [ $sql_bdd_type == "mysql" ]
then
    if [ $sql_is_local == "Y" ]
    then
    apt-get -y install mysql-server
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
    if [ $sql_is_local == "Y" ]
    then
    apt-get -y install postgresql-server
    fi
    apt-get -y install postgresql-client
fi 

if [ $ldap_is_local == "Y" ]
then
apt-get -y install slapd

echo "Hashage du mot de passe ldap..."
hashed_ldap_passwd=$(slappasswd -s ldap_password)

echo $hashed_ldap_passwd
echo "Formatage des fichiers de config ldap"
sed 's/dc=example,dc=org/'"$ldap_dn"'/g' install_utils/db.ldiff | sed 's/FILL_IT/'"$hashed_ldap_passwd"'/g' > /tmp/db
sed 's/dc=example,dc=org/'"$ldap_dn"'/g' install_utils/schema.ldiff | sed 's/FILL_IT/'"$hashed_ldap_passwd"'/g' > /tmp/schema

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

else
echo "Vous devrez manuellement effectuer les opérations de setup de la base ldap sur le serveurs distant.
Le mot de passe ldap a été placé dans le fichier re2o/settings_local"
fi

echo "Ecriture de settings_local"

django_secret_key=$(python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])')

cp re2o/settings_local.example.py re2o/settings_local.py
#sed -i 's/SUPER_SECRET_KEY/'"$django_secret_key"'/g' re2o/settings_local.py
sed -i 's/SUPER_SECRET_DB/'"$sql_password"'/g' re2o/settings_local.py
sed -i 's/db_name_value/'"$sql_name"'/g' re2o/settings_local.py
sed -i 's/db_user_value/'"$sql_login"'/g' re2o/settings_local.py
sed -i 's/db_host_value/'"$sql_host"'/g' re2o/settings_local.py
sed -i 's/ldap_dn/'"$ldap_cn"'/g' re2o/settings_local.py
sed -i 's/SUPER_SECRET_LDAP/'"$ldap_password"'/g' re2o/settings_local.py
sed -i 's/ldap_host_ip/'"$ldap_host"'/g' re2o/settings_local.py
sed -i 's/dc=example,dc=org/'"$ldap_dn"'/g' re2o/settings_local.py
sed -i 's/example.org/'"$extension_locale"'/g' re2o/settings_local.py

echo "Application des migrations"
#python3 manage.py migrate

