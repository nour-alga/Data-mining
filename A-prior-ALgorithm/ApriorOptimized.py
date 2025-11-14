from itertools import combinations
from collections import defaultdict

class AprioriOptimizedFast:
    def __init__(self, transactions, support):
        self.transactions = transactions
        self.support = support
        self.L = {}  # dictionnaire pour stocker les itemsets fréquents par taille k
    
    # -----------------------------
    # Pass 1 : items fréquents (L1)
    # -----------------------------
    def pass1(self):
        """
        Premier passage : compter tous les items uniques et garder ceux avec support >= s
        """
        item_count = defaultdict(int)
        for basket in self.transactions:
            for item in basket:
                item_count[item] += 1
        
        # L1 = items fréquents (support >= seuil)
        frequent_items = [(item,) for item, count in item_count.items() if count >= self.support]
        self.L[1] = {item: item_count[item[0]] for item in frequent_items}
        return frequent_items
    
    # -----------------------------
    # Génération des candidats Ck à partir de L(k-1)
    # Pipeline: L_{k-1} -> C_k (candidates)
    # -----------------------------
    def generate_candidates(self, prev_frequent, k):
        """
        Génère les candidats k-itemsets (Ck) à partir des itemsets fréquents (k-1)
        Utilise la méthode de jointure F_{k-1} × F_{k-1} du livre MMDS
        """
        candidates = set()
        prev_frequent_sorted = sorted([tuple(sorted(x)) for x in prev_frequent])
        prev_frequent_set = set(prev_frequent_sorted)
        
        n = len(prev_frequent_sorted)
        
        for i in range(n):
            for j in range(i + 1, n):
                itemset1 = prev_frequent_sorted[i]
                itemset2 = prev_frequent_sorted[j]
                
                # Jointure selon MMDS: les k-2 premiers éléments doivent être identiques
                if itemset1[:-1] == itemset2[:-1]:  # Partage des k-2 premiers éléments
                    # Créer le candidat en fusionnant les deux itemsets
                    candidate = tuple(sorted(set(itemset1) | set(itemset2)))
                    
                    # Pruning: tous les sous-itemsets de taille k-1 doivent être fréquents
                    if all(tuple(sorted(sub)) in prev_frequent_set for sub in combinations(candidate, k-1)):
                        candidates.add(candidate)
        
        return list(candidates)
    
    # -----------------------------
    # Pass k : C_k -> L_k
    # Pipeline: compter le support de Ck, filtrer pour obtenir Lk
    # -----------------------------
    def passk_fast(self, prev_frequent, k):
        """
        Passage k de l'algorithme A-Priori:
        1. Générer Ck (candidats) à partir de L_{k-1}
        2. Compter le support de chaque candidat
        3. Filtrer Ck -> Lk (garder seulement support >= s)
        """
        if k < 2:
            raise ValueError("k must be >= 2")
        
        # Étape 1: Générer Ck (candidats)
        candidates = self.generate_candidates(prev_frequent, k)
        
        if not candidates:
            return []
        
        candidates_set = set(candidates)
        k_count = defaultdict(int)
        
        # Optimisation: extraire tous les items fréquents de L_{k-1}
        # Cela évite de générer des combinaisons inutiles dans les baskets
        frequent_items = set()
        for itemset in prev_frequent:
            frequent_items.update(itemset)
        
        # Étape 2: Compter le support de chaque candidat dans Ck
        for basket in self.transactions:
            # Filtrer le basket pour ne garder que les items fréquents
            basket_items = [item for item in basket if item in frequent_items]
            
            # Si le basket filtré est trop petit, passer au suivant
            if len(basket_items) < k:
                continue
            
            # Générer tous les k-subsets du basket filtré
            for subset in combinations(basket_items, k):
                subset = tuple(sorted(subset))
                # Vérifier si ce subset est un candidat
                if subset in candidates_set:
                    k_count[subset] += 1
        
        # Étape 3: Filtrer Ck -> Lk (garder seulement support >= s)
        frequent_k_items = [itemset for itemset, count in k_count.items() if count >= self.support]
        self.L[k] = {itemset: k_count[itemset] for itemset in frequent_k_items}
        
        return frequent_k_items
    
    # -----------------------------
    # Méthode principale pour exécuter l'algorithme complet
    # -----------------------------
    def run(self, max_k=None):
        """
        Exécute l'algorithme A-Priori complet
        Retourne tous les itemsets fréquents trouvés
        """
        print(f"Running A-Priori with support threshold = {self.support}")
        
        # Pass 1
        print("Pass 1: Finding frequent 1-itemsets...")
        L_prev = self.pass1()
        print(f"  Found {len(L_prev)} frequent 1-itemsets")
        
        k = 2
        while L_prev and (max_k is None or k <= max_k):
            print(f"Pass {k}: Finding frequent {k}-itemsets...")
            L_k = self.passk_fast(L_prev, k)
            
            if not L_k:
                print(f"  No frequent {k}-itemsets found. Stopping.")
                break
            
            print(f"  Found {len(L_k)} frequent {k}-itemsets")
            L_prev = L_k
            k += 1
        
        return self.L