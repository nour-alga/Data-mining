from Shingling import Shingling
class CompareSets:
    def __init__(self):
        pass

    def union(self, v1, v2):
        return list(set(v1 + v2))

    def inter(self, v1, v2):
        inter = []
        for i in v1:
            if i in v2:
                inter.append(i)
        return list(set(inter))

    def jaccard_similarity(self, v1, v2):
        union_set = self.union(v1, v2)
        inter_set = self.inter(v1, v2)
        return len(inter_set) / len(union_set)
    

    