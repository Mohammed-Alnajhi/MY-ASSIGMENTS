from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import os
import socket

print("=" * 80)
print(" GOLD AGGREGATION - STAR SCHEMA")
print("=" * 80)

try:
    import pyspark
except Exception as e:
    raise RuntimeError(f"PySpark is not available in this Python environment: {e}")

driver_host = socket.gethostbyname("spark-master")
spark_master = os.getenv("SPARK_MASTER", "spark://spark-master:7077")

spark = SparkSession.builder \
    .appName("GoldStarSchema") \
    .master(spark_master) \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.driver.host", driver_host) \
    .config("spark.driver.bindAddress", "0.0.0.0") \
    .config("spark.driver.port", "0") \
    .config("spark.blockManager.port", "0") \
    .config("spark.ui.port", "0") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

print(" Spark session created")


silver_path = "hdfs://namenode:9000/user/hive/warehouse/silver/cleaned_incidents/combined_2025_data_2025.parquet"
silver_df = spark.read.parquet(silver_path)

print(f" Silver: {silver_df.count():,} records")

dim_type_df = silver_df \
    .select("incident_type_clean", "source") \
    .distinct() \
    .withColumn("type_id", monotonically_increasing_id() + 1) \
    .withColumnRenamed("incident_type_clean", "type_name") \
    .withColumnRenamed("source", "category")

print(f"    dim_incident_type: {dim_type_df.count():,} unique types")

dim_location_df = silver_df \
    .select("city") \
    .distinct() \
    .withColumn("location_id", monotonically_increasing_id() + 1)

print(f"    dim_location: {dim_location_df.count():,} unique locations")

fact_df = silver_df \
    .join(
        dim_type_df, 
        (silver_df.incident_type_clean == dim_type_df.type_name) & (silver_df.source == dim_type_df.category), 
        "inner"
    ) \
    .join(
        dim_location_df, 
        silver_df.city == dim_location_df.city, 
        "inner"
    ) \
    .select(
        col("incident_id"),
        col("incident_date_clean").alias("incident_date"),
        col("type_id"),
        col("location_id"),
        col("latitude"),
        col("longitude")
    )

print(f"    fact_incidents: {fact_df.count():,} records")

gold_base_path = "hdfs://namenode:9000/user/hive/warehouse/gold/"

dim_type_df.write.mode("overwrite").parquet(gold_base_path + "dim_incident_type.parquet")
print("    Saved dim_incident_type.parquet")

dim_location_df.write.mode("overwrite").parquet(gold_base_path + "dim_location.parquet")
print("    Saved dim_location.parquet")

fact_df.write.mode("overwrite").parquet(gold_base_path + "fact_incidents.parquet")
print("    Saved fact_incidents.parquet")

print("\n GOLD COMPLETE!")