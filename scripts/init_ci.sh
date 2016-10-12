apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip

#aggiungo l'utente ted nel sistema operativo
adduser ted
#lo creo a livello di postgres
createuser -P -s -e ted
#creo il db
psql -c "CREATE DATABASE triviapatente"
psql -c "CREATE DATABASE triviapatente_test "
#do il privilegio all'utente ted
psql -c "GRANT ALL PRIVILEGES ON DATABASE triviapatente TO ted"
psql -c "GRANT ALL PRIVILEGES ON DATABASE triviapatente_test TO ted"
