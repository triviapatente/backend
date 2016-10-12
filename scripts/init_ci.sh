apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip

#aggiungo l'utente ted nel sistema operativo
adduser ted
#lo creo a livello di postgres
sudo -u postgres bash -c "createuser -P -s -e ted"
#creo il db
sudo -u postgres bash -c "psql -c \"CREATE DATABASE triviapatente \""
sudo -u postgres bash -c "psql -c \"CREATE DATABASE triviapatente_test \""
#do il privilegio all'utente ted
sudo -u postgres bash -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE triviapatente TO ted\""
sudo -u postgres bash -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE triviapatente_test TO ted\""
