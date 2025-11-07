from collections import defaultdict


class LSH:
    def __init__(self , num_bandes):
        self.bandes = []
        self.num_bandes = num_bandes

    def split_bandes(self, signature, bands):
        self.bandes = []  # réinitialiser les bandes
        n = len(signature)
        rows = n // bands   # lignes par bande

        for i in range(bands):
            start = i * rows
            end = start + rows
            self.bandes.append(signature[start:end])

        return self.bandes
    def LSH (self ,  signatures , bands):
        n_docs = len(signatures)
        all_bandes = []
        for i in range(n_docs) :
            all_bandes.append(split_bandes(self , signatures[i], bands))
        candidat_pairs = set()
    # parcourir chaque bande 
        for band_ind in bands :
            buckets =  defaultdict(list)        
            for doc_index in range(n_docs)  : 
                workingband= all_bandes[doc_index][band_ind]
                h = hash(tuple(workingband)) 
                buckets[h].append(doc_index) 
            for bucket_docs in buckets.values():
                 if len(bucket_docs) > 1:  # plus d'un doc → candidats
                     for i in range(len(bucket_docs)):
                        for j in range(i+1, len(bucket_docs)):
                            candidat_pairs.add((bucket_docs[i], bucket_docs[j]))

        

            