"""from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType

# starting a spark session 
spark = SparkSession.builder \
    .appName("Shingling with PySpark") \
    .getOrCreate() """
import random

class Shingling:
    def __init__(self, k):
        self.k = k
        self.shingles = []
         

    # Character shingles
    def create_shingles_char(self, text):
        self.shingles = [text[i:i+self.k] for i in range(len(text)-self.k+1)]
        return self.shingles

    # Word shingles
    def create_shingles_word(self, text):
        words = text.split()
        self.shingles = [" ".join(words[i:i+self.k]) for i in range(len(words)-self.k+1)]
        return self.shingles

    # Hashing shingles
    def hashing(self):
        hashed_shingles = [hash(s) % 2**32 for s in self.shingles]  # modulo to limit the size 
        return hashed_shingles


"""#try 
doc = "Hello Nour how are you i'm fine and you / whatever : let's try these caracteres "
sh = Shingling(k=2)

# Word shingles
print(sh.create_shingles_word(doc))
print(sh.hashing())
# / : considered as a word ' not a word 

# Character shingles
#sh.k = 7
print(sh.create_shingles_char(doc))
print(sh.hashing())
"""