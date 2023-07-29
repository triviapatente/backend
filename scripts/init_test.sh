#script utilizzato per l'inizializzazione del db di test

sudo -u postgres bash -c "psql -c \"CREATE DATABASE triviapatente_test\""
sudo -u postgres bash -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE triviapatente_test TO triviapatente\""
