import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import zlib
import random
from Shingling import Shingling
from Comparesignature import Comparesignature

# -----------------------------
# MinHashing class (deterministic)
# -----------------------------
class MinHashing:
    def __init__(self, num_hashes=100, seed=42):
        self.num_hashes = num_hashes
        self.max_hash = 2**32 - 1
        self.prime = 4294967311  # large prime number
        random.seed(seed)  # fix randomness
        self.hash_funcs = [
            (random.randint(1, self.prime - 1), random.randint(0, self.prime - 1))
            for _ in range(num_hashes)
        ]

    def compute_signature(self, hashed_shingles):
        signature = []
        for a, b in self.hash_funcs:
            min_hash_val = self.max_hash
            for shingle in hashed_shingles:
                hash_val = (a * shingle + b) % self.prime
                if hash_val < min_hash_val:
                    min_hash_val = hash_val
            signature.append(min_hash_val)
        return signature

# -----------------------------
# LSH class (deterministic)
# -----------------------------
class LSH:
    def __init__(self, num_bandes, threshold=1.0):
        self.num_bandes = num_bandes
        self.threshold = threshold

    def split_bandes(self, signature):
        n = len(signature)
        rows = max(1, n // self.num_bandes)
        bandes = []
        for i in range(self.num_bandes):
            start = i * rows
            end = min(start + rows, n)
            bandes.append(signature[start:end])
        return bandes

    def get_candidates(self, signatures):
        n_docs = len(signatures)
        all_bandes = [self.split_bandes(sig) for sig in signatures]
        candidate_pairs = set()

        for band_ind in range(self.num_bandes):
            buckets = defaultdict(list)
            for doc_index in range(n_docs):
                workingband = all_bandes[doc_index][band_ind]
                if len(workingband) == 0:
                    continue
                # deterministic hash
                h = zlib.crc32(bytes(str(tuple(map(int, workingband))), encoding='utf8'))
                buckets[h].append(doc_index)

            # generate candidate pairs
            for bucket_docs in buckets.values():
                if len(bucket_docs) > 1:
                    for i in range(len(bucket_docs)):
                        for j in range(i + 1, len(bucket_docs)):
                            candidate_pairs.add((bucket_docs[i], bucket_docs[j]))

        return candidate_pairs

    def filter_candidates(self, signatures, candidates):
        filtered = set()
        for i, j in candidates:
            sim = Comparesignature.CompareSignatures(signatures[i], signatures[j])
            if sim >= self.threshold:
                filtered.add((i, j))
        return filtered

    def run(self, signatures):
        candidates = self.get_candidates(signatures)
        return self.filter_candidates(signatures, candidates)

# -----------------------------
# Load data
# -----------------------------
file_path = "../archive(1)/Articles.csv"
df = pd.read_csv(file_path, encoding='latin1')
documents = df['Article'].tolist()[:1000]
print("Nombre de documents utilisés:", len(documents))

# -----------------------------
# Parameters
# -----------------------------
k = 2
num_hashes = 20
num_bands = 5
threshold = 0.8

# -----------------------------
# Create signatures
# -----------------------------
sh = Shingling(k=k)
mh = MinHashing(num_hashes=num_hashes, seed=42)

signatures = []
for doc in documents:
    shingles = sh.create_shingles_word(doc)
    hashed_shingles = sh.hashing()
    sig = mh.compute_signature(hashed_shingles)
    signatures.append(sig)

# -----------------------------
# Run LSH
# -----------------------------
lsh = LSH(num_bandes=num_bands, threshold=threshold)
candidate_pairs = lsh.run(signatures)
print("Candidate pairs from LSH:", len(candidate_pairs))

# -----------------------------
# Functions for plots (deterministic)
# -----------------------------
def test_num_bands(signatures, band_list, threshold=0.8):
    results = []
    for nb in band_list:
        lsh = LSH(num_bandes=nb, threshold=threshold)
        candidates = lsh.run(signatures)
        results.append(len(candidates))
    plt.figure(figsize=(8,5))
    plt.plot(band_list, results, marker='o')
    plt.xlabel("Number of Bands")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Number of Bands on Candidate Pairs")
    plt.show()

def test_threshold(signatures, thresholds, num_bandes=5):
    results = []
    for th in thresholds:
        lsh = LSH(num_bandes=num_bandes, threshold=th)
        candidates = lsh.run(signatures)
        results.append(len(candidates))
    plt.figure(figsize=(8,5))
    plt.plot(thresholds, results, marker='o', color='green')
    plt.xlabel("Threshold")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Threshold on Candidate Pairs")
    plt.show()

def test_num_hashes(documents, hash_list, k=2, num_bandes=5, threshold=0.8, seed=42):
    results = []
    sh = Shingling(k=k)
    for nh in hash_list:
        mh = MinHashing(num_hashes=nh, seed=seed)
        signatures = []
        for doc in documents:
            shingles = sh.create_shingles_word(doc)
            hashed_shingles = sh.hashing()
            sig = mh.compute_signature(hashed_shingles)
            signatures.append(sig)
        lsh = LSH(num_bandes=num_bandes, threshold=threshold)
        candidates = lsh.run(signatures)
        results.append(len(candidates))
    plt.figure(figsize=(8,5))
    plt.plot(hash_list, results, marker='o', color='red')
    plt.xlabel("Number of Hash Functions")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Number of Hash Functions on Candidate Pairs")
    plt.show()

# -----------------------------
# Run deterministic tests
# -----------------------------
band_list = [2, 3, 5, 10, 20]
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
hash_list = [10, 20, 50, 100]

test_num_bands(signatures, band_list)
test_threshold(signatures, thresholds)
test_num_hashes(documents, hash_list)
