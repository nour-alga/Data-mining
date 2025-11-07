import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from Shingling import Shingling
from MinHashing import MinHashing
#file path 
file_path1 = "../sentiment+labelled+sentences/sentiment labelled sentences/imdb_labelled.txt"
file_path2 = "../sentiment+labelled+sentences/sentiment labelled sentences/amazon_cells_labelled.txt"

# Load into pandas
doc1 = pd.read_csv(file_path1, sep='\t', header=None, names=['sentence', 'label'])
doc2 = pd.read_csv(file_path2, sep='\t', header=None, names=['sentence', 'label'])
doc1 = doc1.drop(columns=['label'])
doc2 = doc2.drop(columns=['label'])
#print(df.head())

# Parameters
k = 2  # word shingles
num_hashes = 50
documents = [
    " ".join(doc1['sentence'].tolist()),  # combine all sentences into one string
    " ".join(doc2['sentence'].tolist())
]
print ("document 1 " , documents[0])
print("document 2 " , documents[1])
# Initialize objects
sh = Shingling(k=k)
mh = MinHashing(num_hashes=num_hashes)

# Compute hashed shingles and MinHash signatures
signatures = []
for doc in documents:
    shingles = sh.create_shingles_word(doc)
    hashed_shingles = sh.hashing()
    sig = mh.compute_signature(hashed_shingles)
    signatures.append(sig)

# Compute pairwise Jaccard similarity from signatures
n = len(signatures)
sim_matrix = [[0]*n for _ in range(n)]

for i in range(n):
    for j in range(n):
        # Count equal values in signatures
        count = sum([1 for a, b in zip(signatures[i], signatures[j]) if a == b])
        sim_matrix[i][j] = count / num_hashes

# Convert to DataFrame for heatmap
sim_df = pd.DataFrame(sim_matrix, index=[f'Doc{i}' for i in range(n)],
                      columns=[f'Doc{i}' for i in range(n)])

# Plot heatmap
plt.figure(figsize=(8,6))
sns.heatmap(sim_df, annot=True, cmap="YlGnBu")
plt.title("Jaccard Similarity (MinHash) Heatmap")
plt.show()

