# Data Processing Module

### Running a local, dokerized Spark cluster

```bash
# Start
docker compose up -d

# Stop
docker compose down
```

### Creating Spark Session in python

Example of pyspark code running parallelized summing operation on the local Spark cluster.

```python
# Import the necessary modules
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Create a SparkSession
spark = SparkSession.builder \
   .appName("My App") \
   .getOrCreate()

rdd = spark.sparkContext.parallelize(range(1, 100))

print("THE SUM IS HERE: ", rdd.sum())
# Stop the SparkSession
spark.stop()
```
