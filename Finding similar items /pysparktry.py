from pyspark.sql import SparkSession

# Initialize a Spark session
spark = SparkSession.builder \
    .appName("PySpark Test") \
    .getOrCreate()

# Test by creating a simple DataFrame
data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
columns = ["name", "value"]

df = spark.createDataFrame(data, columns)

# Show the DataFrame
df.show()
