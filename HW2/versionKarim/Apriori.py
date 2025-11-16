from collections import Counter
from itertools import combinations

def baskets(path):
    with open(path) as f:
        for line in f:
            yield tuple(map(int, line.split()))

def apriori_gen(Lk):
    L = list(Lk)
    k = len(L[0]) + 1
    Ck = set()
    for i in range(len(L)):
        for j in range(i+1, len(L)):
            a, b = L[i], L[j]
            union = a | b
            if len(union) == k:
                if all(frozenset(sub) in Lk for sub in combinations(union, k-1)):
                    Ck.add(union)
    return Ck

def count_support(candidates, path, k):
    """ support counting using combinations of baskets."""
    candidate_set = set(candidates)
    counter = Counter()

    for t in baskets(path):
        # generate only k-combinations from this transaction
        for combo in combinations(t, k):
            fs = frozenset(combo)
            if fs in candidate_set:
                counter[fs] += 1

    return counter

def apriori(path, min_sup):
    # L1
    counts = Counter()
    for t in baskets(path):
        for item in t:
            counts[frozenset([item])] += 1

    Lk = {i: s for i, s in counts.items() if s >= min_sup}
    all_freq = dict(Lk)

    k = 2
    while Lk:
        Ck = apriori_gen(Lk)
        if not Ck:
            break

        supports = count_support(Ck, path, k)
        Lk = {c: s for c, s in supports.items() if s >= min_sup}
        all_freq.update(Lk)

        k += 1

    return all_freq

def generate_rules(frequent_itemsets, min_conf):
    """
    frequent_itemsets: dict mapping frozenset -> support
    min_conf: minimum confidence threshold (float in [0,1])
    """
    rules = []

    # iterate over itemsets with size ≥ 2
    for itemset, sup_itemset in frequent_itemsets.items():
        if len(itemset) < 2:
            continue

        items = list(itemset)

        # generate all non-empty proper subsets
        for r in range(1, len(items)):
            for X in combinations(items, r):
                X = frozenset(X)
                Y = itemset - X

                sup_X = frequent_itemsets.get(X)
                if sup_X is None:
                    continue

                conf = sup_itemset / sup_X

                if conf >= min_conf:
                    rules.append((X, Y, sup_itemset, conf))

    return rules


def sort_key(pair):
    itemset, support = pair
    return (-len(itemset), -support)

if __name__ == "__main__":
    path = "T10I4D100K.dat"
    min_sup = 1000
    min_conf = 0.6 

    frequent = apriori(path, min_sup)

    print(f"\nFound {len(frequent)} frequent itemsets with support ≥ {min_sup}.\n")
    for itemset, support in sorted(frequent.items(), key=sort_key):
        print(f"{set(itemset)} : {support}")

    # association rule generation
    rules = generate_rules(frequent, min_conf)

    print(f"\nGenerated {len(rules)} association rules with confidence ≥ {min_conf}:\n")
    for X, Y, sup, conf in rules:
        print(f"{set(X)} => {set(Y)}  (support={sup}, confidence={conf:.3f})")
