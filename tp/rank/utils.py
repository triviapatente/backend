from flask import g
from tp.auth.models import User

def extractArrayFrom(left, right, limit):
    left_min = len(left) < limit / 2
    right_min = len(right) < limit / 2
    sum_min = len(left) + len(right) < limit
    output = []
    #entrambi hanno meno di (##limit / 2) elementi a testa
    if (left_min and right_min) or sum_min:
        #ritorno un risultato con lunghezza < ##limit
        output = left + right
    #l'array di sinistra ha meno di (##limit / 2) elementi
    elif left_min:
        #dall'array di destra prendo (##limit - gli elementi di sinistra) elementi
        upper_bound = limit - len(left)
        #prendo tutti quelli da sinistra
        output = left + right[:upper_bound]
    #l'array di destra ha meno di 5 elementi
    elif right_min:
        #dall'array di sinistra prendo (##limit - gli elementi di destra) elementi
        lower_bound = len(left) - (limit - len(right))
        #prendo tutti quelli da destra
        output = left[lower_bound:] + right
    #entrambi gli array hanno un numero di elementi >= a (##limit / 2)
    else:
        #prendo gli ultimi (##limit / 2) elementi da quello di sinistra, e i primi (##limit / 2) da destra
        lower_bound = len(left) - (limit / 2)
        upper_bound = limit / 2
        output = left[lower_bound:] + right[:upper_bound]
    return output

def insertUser(user, rank):
    for i in range(0, len(rank)):
        if rank[i].internalPosition > user.internalPosition:
            rank.insert(i, user)
            return rank
    return rank
