from collections import defaultdict
from math import ceil
from Comparesignature import Comparesignature
import zlib



class LSH:
    def __init__(self, num_bandes, threshold=1.0):
        self.num_bandes = num_bandes
        self.threshold = threshold  # Threshold for filtering final pairs

    def split_bandes(self, signature):
        n = len(signature)
        rows = ceil(n / self.num_bandes)  # ceil is safer than integer division
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
                # Stable hash using zlib.crc32
                h = zlib.crc32(bytes(str(tuple(map(int, workingband))), encoding='utf8'))
                buckets[h].append(doc_index)

            # Form candidate pairs
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


