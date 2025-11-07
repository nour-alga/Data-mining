"""from Shingling import Shingling
from CompareSets import CompareSets
from MinHashing import MinHashing

# --- Documents to compare ---
doc1 = "Hello Nour how are you"
doc2 = "Hello Nour I’m fine thank you"

# --- Create shingles (word-based) ---
sh1 = Shingling(k=2)
sh2 = Shingling(k=2)

hashed1 = sh1.hashing() if sh1.create_shingles_word(doc1) else []
hashed2 = sh2.hashing() if sh2.create_shingles_word(doc2) else []

# --- Display shingles and their hashes ---
print("=== Document 1 ===")
print("Word shingles:", sh1.shingles)
print("Hashed shingles:", hashed1)
print()
print("=== Document 2 ===")
print("Word shingles:", sh2.shingles)
print("Hashed shingles:", hashed2)
print()

# --- Create MinHash signatures ---
mh = MinHashing(num_hashes=10)  # you can change 10 → 50

sig1 = mh.compute_signature(hashed1)
sig2 = mh.compute_signature(hashed2)

# --- Display signature vectors ---
print("=== MinHash Signatures ===")
print("Signature (Doc1):", sig1)
print("Signature (Doc2):", sig2)
print()

# --- Compare signatures ---
similarity = sum([1 for i in range(len(sig1)) if sig1[i] == sig2[i]]) / len(sig1)
print(f"Estimated Jaccard similarity (based on signatures): {similarity:.3f}")"""
