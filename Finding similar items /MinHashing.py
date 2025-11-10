import random
from CompareSets import CompareSets

class MinHashing:
    def __init__(self, num_hashes=100):
        self.num_hashes = num_hashes
        self.max_hash = 2**32 - 1
        self.prime = 4294967311  # a large prime number 
        # Generate random coefficients for hash functions
        random.seed(42)
        self.hash_funcs = [
            (random.randint(1, self.prime - 1), random.randint(0, self.prime - 1))
            for _ in range(num_hashes)
        ]

    def compute_signature(self, hashed_shingles):

        signature = []
        for a, b in self.hash_funcs:
            min_hash_val = self.max_hash
            for shingle in hashed_shingles:
                # compute hash function value for this shingle
                hash_val = (a * shingle + b) % self.prime
                if hash_val < min_hash_val:
                    min_hash_val = hash_val
            signature.append(min_hash_val)
        return signature
    
class Comparesignature : 
    def __init__(self):
         pass 
    def CompareSignatures (vec1 , vec2 ):
        assert len(vec1)== len(vec2)
        count = 0 
        for i in range(len(vec1)) :
            if vec1[i]==vec2[i] :
                count+=1 
        return count/len(vec1)

