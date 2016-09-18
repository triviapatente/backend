#distruggo vagrant
vagrant destroy
#sposto il Vagrantfile, dato che la inizializzazione richede sia rimosso ma noi lo vogliamo mantenere
mv -f Vagrantfile .Vagrantfile
#lo reinizializzo con la giusta versione di ubuntu
vagrant init ubuntu/trusty32
#riposiziono il vecchio Vagrantfile al suo posto
rm -f Vagrantfile
mv -f .Vagrantfile Vagrantfile
#avvio la macchina virtuale
vagrant up
