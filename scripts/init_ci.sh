apt-get -qqy update
apt-get -qqy install python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip

#aggiungo l'utente con la password già inserita (e crittata)
useradd -p $(echo ted | openssl passwd -1 -stdin) ted
