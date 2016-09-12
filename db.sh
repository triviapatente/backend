#postgresql
#creo utente postgres
sudo -u postgres bash -c "createuser -P -s -e ted"
sudo -u postgres bash -c "psql -c \"CREATE DATABASE triviapatente \""
#cd /etc/postgresql/9.3/main/

#LINE='host all all all password'
#FILE=/etc/postgresql/9.3/main/pg_hba.conf
#sudo grep -q "$LINE" "$FILE" || echo "$LINE" >> "$FILE"


#LINE='listen_addresses = '*''
#FILE=/etc/postgresql/9.3/main/postgresql.conf
#sudo grep -q "$LINE" "$FILE" || echo "$LINE" >> "$FILE"

#sudo /etc/init.d/postgresql restart
#Se vuoi analizzare il tuo db da un tool grafico nella macchina host (fuori da Vagrant)
#Aggiungi questa linea nel vagrantfile   config.vm.network "forwarded_port", guest: 5432, host: 5555
#Scrivi nella macchina host nella cartella del progetto 'vagrant reload' e dai invio (per riavviare vagrant)
#Connettiti col tool grafico all'indirizzo localhost:5555, username root, password root, db triviapatente
#python dependencies
