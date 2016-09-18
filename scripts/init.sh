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
#do il privilegio all'utente ted
sudo -u postgres bash -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE triviapatente TO ted\""

#questi 6 linee di codice ricercano questi pattern nei file e se non lo trovano lo inseriscono
#i commenti sono fondamentali per evidenziare che questi sono i comandi che abbiamo inserito noi
#non rimuovere i commenti
LINE='host all all all password #enable all requests to this machine'
FILE=/etc/postgresql/9.3/main/pg_hba.conf
sudo grep -q "$LINE" "$FILE" || echo "$LINE" >> "$FILE"

#riga che va nel file postgresql.conf e sostituisce la riga preinserita #listen_addresses = 'localhost' con listen_addresses = '*'
sed -i -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/9.3/main/postgresql.conf

#restart del servizio per rendere le modifiche sui due file effettive
sudo /etc/init.d/postgresql restart
#ritorno alla directory di partenza
cd /vagrant