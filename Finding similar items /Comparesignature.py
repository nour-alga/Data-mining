class Comparesignature:
    def __init__(self):
        pass

    @staticmethod
    def CompareSignatures(vec1, vec2):
        assert len(vec1) == len(vec2)
        count = 0
        for i in range(len(vec1)):
            if vec1[i] == vec2[i]:
                count += 1
        return count / len(vec1)
