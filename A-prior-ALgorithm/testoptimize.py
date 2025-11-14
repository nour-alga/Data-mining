import pandas as pd 
from ApriorOptimized import AprioriOptimizedFast

 
# lecture fichier .dat
transactions = []
with open("T10I4D100K.dat", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            transactions.append(list(map(int, line.split())))

"""ap = AprioriOptimizedFast(transactions, support=2)  # tester d'abord sur 1000 transactions
L1 = ap.pass1()
print("Frequent 1-itemsets:", L1[:10])
L2 = ap.passk_fast(L1, 2)
print("Frequent 2-itemsets:", L2[:10])
L3 = ap.passk_fast(L2, 3)
print("Frequent 3-itemsets:", L3[:10])"""
# Execution 
ap2 = AprioriOptimizedFast(transactions, support=1000)
all_frequent = ap2.run(max_k=5) 