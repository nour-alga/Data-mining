from itertools import combinations
from collections import defaultdict

class Apriori:
    def __init__(self, transactions, support):
        self.transactions = transactions
        self.support = support
        self.L = {}
    
    def pass1(self):
        """
        First pass: we  count all unique items and keep those with support >= threshold
        """
        item_count = defaultdict(int)
        for basket in self.transactions:
            for item in basket:
                item_count[item] += 1
        
        frequent_items = [(item,) for item, count in item_count.items() if count >= self.support]
        self.L[1] = {item: item_count[item[0]] for item in frequent_items} #we stock them for later to have all the frequent items in each pass 
        return frequent_items
    
    def generate_candidates(self, prev_frequent, k):
        """
        Generate candidate k-itemsets from frequent (k-1)-itemsets
        
        """
        candidates = set()
        prev_frequent_sorted = sorted([tuple(sorted(x)) for x in prev_frequent])
        prev_frequent_set = set(prev_frequent_sorted)
        
        n = len(prev_frequent_sorted)
        
        for i in range(n):
            for j in range(i + 1, n):
                itemset1 = prev_frequent_sorted[i]
                itemset2 = prev_frequent_sorted[j]
                
                # here we satistfy the condition where  first k-2 elements must be the same
                if itemset1[:-1] == itemset2[:-1]:
                    candidate = tuple(sorted(set(itemset1) | set(itemset2)))
                    
                    # Pruning: all (k-1)-subsets must be frequent
                    if all(tuple(sorted(sub)) in prev_frequent_set for sub in combinations(candidate, k-1)):
                        candidates.add(candidate)
        
        return list(candidates)
    
    def passk(self, prev_frequent, k):
        """
        Pass k of A-Priori algorithm we generalise the algorithme of pass 1 :
        1. Generate candidates Ck from L(k-1)
        2. Count support of each candidate
        3. Filter Ck -> Lk (keep only support >= threshold)
        """
        if k < 2:
            raise ValueError("k must be >= 2")
        
        candidates = self.generate_candidates(prev_frequent, k)
        
        if not candidates:
            return []
        
        candidates_set = set(candidates)
        k_count = defaultdict(int)
        
        # extract all frequent items from L(k-1)
        frequent_items = set()
        for itemset in prev_frequent:
            frequent_items.update(itemset)
        
        # Count support of each candidate in baskets of transactions (data)
        for basket in self.transactions:
            basket_items = [item for item in basket if item in frequent_items]
            
            if len(basket_items) < k:
                continue
            
            for subset in combinations(basket_items, k):
                subset = tuple(sorted(subset))
                if subset in candidates_set:
                    k_count[subset] += 1
        
        #  finally wwe filter Ck -> Lk (keep only support >= threshold)
        frequent_k_items = [itemset for itemset, count in k_count.items() if count >= self.support]
        self.L[k] = {itemset: k_count[itemset] for itemset in frequent_k_items}
        
        return frequent_k_items
    
    def run(self, max_k=None):
        """
        now we ran our algorithme until there is no frequent itemset left 
        """
        print(f"Running A-Priori with support threshold = {self.support}")
        
        print("Pass 1: Finding frequent 1-itemsets")
        L_prev = self.pass1()
        print(f"  Found {len(L_prev)} frequent 1-itemsets")
        
        k = 2
        while L_prev and (max_k is None or k <= max_k):
            print(f"Pass {k}: Finding frequent {k}-itemsets")
            L_k = self.passk(L_prev, k)
            
            if not L_k:
                print(f"  No frequent {k}-itemsets found. Stopping.")
                break
            
            print(f"  Found {len(L_k)} frequent {k}-itemsets")
            L_prev = L_k
            k += 1
        
        return self.L


class AssociationRulesGenerator:
    def __init__(self, frequent_itemsets, c):
        """
        Args:
            frequent_itemsets: dictionary L from A-Priori {k: {itemset: count}}
            c: minimum confidence threshold
        """
        self.L = frequent_itemsets
        self.c = c
    
    def generate_rules(self, verbose=False):
        """
        Generate all association rules with confidence >= c
        
        """
        # Combine all itemsets from all passes into a single dictionary
        all_itemsets = {}
        for k in self.L.keys():
            for itemset, count in self.L[k].items():
                all_itemsets[frozenset(itemset)] = count
        
        # Generate rules from itemsets with size >= 2
        association_rules = defaultdict(set)
        for itemset in filter(lambda x: len(x) > 1, all_itemsets.keys()):
            # For each possible antecedent size
            for antecedent_length in range(1, len(itemset)):
                # For each possible antecedent combination
                for antecedent in [frozenset(comb) for comb in combinations(itemset, antecedent_length)]:
                    if antecedent not in all_itemsets:
                        continue
                    
                    # Calculate confidence: conf(X => Y) = support(X ∪ Y) / support(X)
                    confidence = all_itemsets[itemset] / all_itemsets[antecedent]
                    
                    if confidence >= self.c:
                        consequent = itemset - antecedent
                        association_rules[antecedent].add(consequent)
                        
                        if verbose:
                            print(f"{set(antecedent)} => {set(consequent)} | conf={confidence:.4f}")
        
        return association_rules


# ===== COMPLETE TEST =====
if __name__ == "__main__":
    # Read baskets from file and stock it in transaction 
    print("=" * 70)
    print("READING FILE")
    print("=" * 70)
    transactions = []
    with open("T10I4D100K.dat", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                transactions.append(list(map(int, line.split())))
    
    print(f"Number of transactions: {len(transactions)}\n")
    
    # Execute A-Priori
    print("=" * 70)
    print("EXECUTING A-PRIORI (all passes)")
    print("=" * 70)
    ap = Apriori(transactions, support=1000)
    all_frequent = ap.run(max_k=5)
    
    print("\n" + "=" * 70)
    print("SUMMARY OF FREQUENT ITEMSETS (from all passes combined)")
    print("=" * 70)
    for k in sorted(all_frequent.keys()):
        print(f"L{k}: {len(all_frequent[k])} itemsets")
    
    # Generate association rules ONLY ONCE at the end
    # Using ALL frequent itemsets from ALL passes (L1 + L2 + L3 + ...)
    print("\n" + "=" * 70)
    print("GENERATING ASSOCIATION RULES (ONLY ONCE, at the end)")
    print("Using ALL frequent itemsets from all passes combined")
    print("=" * 70)
    rule_gen = AssociationRulesGenerator(all_frequent, c=0.6)
    rules = rule_gen.generate_rules(verbose=True)
    
    print("\n" + "=" * 70)
    print("SUMMARY OF ASSOCIATION RULES")
    print("=" * 70)
    total_rules = sum(len(v) for v in rules.values())
    print(f"Total: {total_rules} rules found with c>=0.6")
 