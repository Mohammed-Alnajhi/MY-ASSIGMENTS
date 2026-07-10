from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import socket
import os

print("=" * 80)
print(" SILVER TRANSFORMATION")
print("=" * 80)

try:
    import pyspark
except Exception as e:
    raise RuntimeError(f"PySpark is not available in this Python environment: {e}")

driver_host = socket.gethostbyname(socket.gethostname())

spark_master = os.getenv("SPARK_MASTER", "spark://spark-master:7077")

spark = SparkSession.builder \
    .appName("SilverTransformation") \
    .master(spark_master) \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.driver.host", driver_host) \
    .config("spark.driver.bindAddress", "0.0.0.0") \
    .config("spark.driver.port", "0") \
    .config("spark.blockManager.port", "0") \
    .config("spark.ui.port", "0") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

print(" Spark session created")

bronze_path = "hdfs://namenode:9000/user/hive/warehouse/bronze/crime_api/2025/"
bronze_df = spark.read.parquet(bronze_path)

print(f" Bronze: {bronze_df.count():,} records")


silver_df = bronze_df \
    .filter(col("incident_id").isNotNull()) \
    .dropDuplicates(["incident_id"]) \
    .filter(col("latitude").isNotNull() & col("longitude").isNotNull()) \
    .withColumn("incident_type_clean", trim(upper(col("incident_type")))) \
    .withColumn("incident_date_clean", coalesce(to_date(from_unixtime(col("incident_date").cast("long") / 1000)), to_date(col("incident_date"))))

print(f" Silver: {silver_df.count():,} records")

silver_path = "hdfs://namenode:9000/user/hive/warehouse/silver/cleaned_incidents/combined_2025_data_2025.parquet"
silver_df.coalesce(1).write.mode("overwrite").parquet(silver_path)

print(f" Saved to: {silver_path}")
print("\n SILVER COMPLETE!")