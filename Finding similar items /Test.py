import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from Shingling import Shingling
from MinHashing import MinHashing
from LSH import LSH
import random
random.seed(42)
# --- Load data ---
file_path = "../archive(1)/Articles.csv"
df = pd.read_csv(file_path, encoding='latin1')

# Limit to 1000 documents for performance
documents = df['Article'].tolist()[:1000]
print("Nombre de documents utilisés:", len(documents))

# --- Parameters ---
k = 2           # word shingles
num_hashes = 20
num_bands = 5

# --- MinHashing ---
sh = Shingling(k=k)
mh = MinHashing(num_hashes=num_hashes)

signatures = []
for doc in documents:
    shingles = sh.create_shingles_word(doc)
    hashed_shingles = sh.hashing()
    sig = mh.compute_signature(hashed_shingles)
    signatures.append(sig)

# --- LSH: find candidate pairs ---
lsh = LSH(num_bandes=num_bands, threshold=0.8)
candidate_pairs = lsh.run(signatures)
print("Candidate pairs from LSH:", candidate_pairs)

# ===============================================================
#                         VISUALISATIONS
# ===============================================================

"""# --- 1. Network plot (LSH candidate pairs) ---
G = nx.Graph()
G.add_nodes_from(range(len(documents)))
G.add_edges_from(candidate_pairs)

plt.figure(figsize=(10, 10))
nx.draw_networkx(
    G,
    node_size=600,
    with_labels=True,
    node_color='lightblue',
    edge_color='gray',
    font_size=10
)
plt.title("LSH Candidate Pairs Network", fontsize=16)
plt.show()

# --- 2. Histogram: number of candidate matches per document ---
candidate_counts = [0] * len(documents)
for i, j in candidate_pairs:
    candidate_counts[i] += 1
    candidate_counts[j] += 1

plt.figure(figsize=(10, 6))
plt.bar(range(len(documents)), candidate_counts, color='coral')
plt.xlabel("Document Index")
plt.ylabel("Number of Candidate Matches")
plt.title("Number of LSH Candidate Matches per Document", fontsize=14)
plt.show()"""
import matplotlib.pyplot as plt

# Function to test effect of number of bands

      
def test_num_bands(signatures, band_list, threshold=0.8):
    results = []
    print(f"Nombre total de signatures: {len(signatures)}")
    print(f"Taille de chaque signature (num_hashes): {len(signatures[0])}")
    print(f"Max paires possibles: {len(signatures)*(len(signatures)-1)//2}")
    print("-" * 50)
    
    for nb in band_list:
        lsh = LSH(num_bandes=nb, threshold=threshold)
        candidates = lsh.get_candidates(signatures)
        rows_per_band = len(signatures[0]) / nb
        print(f"Bands: {nb}, Rows/band: {rows_per_band:.1f}, Candidats: {len(candidates)}")
        results.append(len(candidates))
    
    plt.figure(figsize=(8,5))
    plt.plot(band_list, results, marker='o')
    plt.xlabel("Number of Bands")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Number of Bands on Candidate Pairs")
    plt.show()

# Function to test effect of threshold
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

# Function to test effect of number of hashes
def test_num_hashes(documents, hash_list, k=2, num_bandes=5, threshold=0.8):
    results = []
    sh = Shingling(k=k)
    for nh in hash_list:
        mh = MinHashing(num_hashes=nh)
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
import time
def test_lsh_execution_time(signatures, band_list, threshold=0.8, num_runs=3):
    """
    Measure LSH execution time with multiple runs for accuracy.
    Takes the average of num_runs executions to account for caching effects.
    """
    execution_times = []
    
    for nb in band_list:
        times = []
        
        # Run multiple times and take average
        for run in range(num_runs):
            lsh = LSH(num_bandes=nb, threshold=threshold)
            
            start_time = time.time()
            candidates = lsh.get_candidates(signatures)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        # Calculate average time
        avg_time = sum(times) / len(times)
        execution_times.append(avg_time)
        print(f"Bands: {nb}, Avg Time: {avg_time:.4f}s (over {num_runs} runs), Candidates: {len(candidates)}")
    
    plt.figure(figsize=(8,5))
    plt.plot(band_list, execution_times, marker='o', color='purple', linewidth=2)
    plt.xlabel("Number of Bands")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("LSH Execution Time vs Number of Bands")
    plt.grid(True, alpha=0.3)
    plt.show()
# -----------------------------
# Run the tests
# -----------------------------
band_list = [2, 3, 5, 6 ]
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
hash_list = [10, 20, 50, 100]

test_num_bands(signatures, band_list)
test_threshold(signatures, thresholds)
test_num_hashes(documents, hash_list)
test_lsh_execution_time(signatures, band_list , num_runs=3)

