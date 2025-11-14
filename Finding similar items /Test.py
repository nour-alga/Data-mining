
import pandas as pd
import matplotlib.pyplot as plt
import random
import time
from collections import defaultdict
from Shingling import Shingling
from MinHashing import MinHashing
from LSH import LSH

# to reduce the randomness of shinging .. 
random.seed(42)

# Loading data that's on the file archive(1) if you change the folder name change it here in the file path before runing the code please
file_path = "archive(1)/Articles.csv"
df = pd.read_csv(file_path, encoding='latin1')

# Limit to 1000 documents 
documents = df['Article'].tolist()[:1000]
print("Number of documents used:", len(documents))

  # parameters 
k = 2                # size of each shingle
num_hashes = 20      # Number of hash functions
num_bands = 5        # Number of bands for LSH
threshold = 0.8      # Similarity threshold

print("\n--- Generating MinHash signatures ---")

sh = Shingling(k=k)
mh = MinHashing(num_hashes=num_hashes)

signatures = []
for doc in documents:
    # Step 1: Create shingles from words
    shingles = sh.create_shingles_word(doc)
    # Step 2: Hash shingles to numerical values
    hashed_shingles = sh.hashing()
    # Step 3: Computing MinHash signature for the document
    sig = mh.compute_signature(hashed_shingles)
    signatures.append(sig)

print("Total signatures generated:", len(signatures))

# LSH 
print("\n--- Running LSH to find candidate pairs ---")

lsh = LSH(num_bandes=num_bands, threshold=threshold)
candidate_pairs = lsh.run(signatures)
print("Candidate pairs found:", candidate_pairs)

# plots for results on eport 

#  Effect of number of bands on candidate pairs

def test_num_bands(signatures, band_list, threshold=0.8):
    
    results = []   
    for nb in band_list:
        lsh = LSH(num_bandes=nb, threshold=threshold)
        candidates = lsh.get_candidates(signatures)
        rows_per_band = len(signatures[0]) / nb
        #print(f"Bands: {nb}, Rows/Band: {rows_per_band:.1f}, Candidates: {len(candidates)}") this for debuging 
        results.append(len(candidates))
    
    # Plot results
    plt.figure(figsize=(8,5))
    plt.plot(band_list, results, marker='o')
    plt.xlabel("Number of Bands")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Number of Bands on Candidate Pairs")
    plt.grid(True, alpha=0.3)
    plt.show()

#  Effect of threshold on candidate pairs

def test_threshold(signatures, thresholds, num_bandes=5):
    results = []
 
    for th in thresholds:
        lsh = LSH(num_bandes=num_bandes, threshold=th)
        candidates = lsh.run(signatures)
        #print(f"Threshold: {th}, Candidate pairs: {len(candidates)}")
        results.append(len(candidates))
    
    plt.figure(figsize=(8,5))
    plt.plot(thresholds, results, marker='o', color='green')
    plt.xlabel("Threshold")
    plt.ylabel("Number of Candidate Pairs")
    plt.title("Effect of Threshold on Candidate Pairs")
    plt.grid(True, alpha=0.3)
    plt.show()


#  Effect of number of hash functions

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
    plt.grid(True, alpha=0.3)
    plt.show()


# LSH execution time vs number of bands

def test_lsh_execution_time(signatures, band_list, threshold=0.8, num_runs=3):

    execution_times = []

    for nb in band_list:
        times = []
        for run in range(num_runs):
            lsh = LSH(num_bandes=nb, threshold=threshold)
            start_time = time.time()
            candidates = lsh.get_candidates(signatures)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        execution_times.append(avg_time)
        
    
    plt.figure(figsize=(8,5))
    plt.plot(band_list, execution_times, marker='o', color='purple', linewidth=2)
    plt.xlabel("Number of Bands")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("LSH Execution Time vs Number of Bands")
    plt.grid(True, alpha=0.3)
    plt.show()

#runing  experiments 
band_list = [2, 3, 5, 6] #because number of hash function is 20 
thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
hash_list = [10, 20, 50, 100]

test_num_bands(signatures, band_list)
test_threshold(signatures, thresholds)
test_num_hashes(documents, hash_list)
test_lsh_execution_time(signatures, band_list, num_runs=3)
