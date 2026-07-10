from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time

print(" Starting Complete Spark Streaming Job...")

spark = SparkSession.builder \
    .appName("PublicSafety_Complete_Streaming") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

schema = StructType([
    StructField("call_id", StringType(), True),
    StructField("incident_type", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("location", StructType([
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True)
    ]), True),
    StructField("priority", StringType(), True),
    StructField("status", StringType(), True),
    StructField("precinct", StringType(), True),
    StructField("description", StringType(), True)
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "emergency_calls") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

parsed_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", schema).alias("data")) \
    .select("data.*")

processed_df = parsed_df \
    .withColumn("incident_date", to_date(col("timestamp"))) \
    .withColumn("incident_hour", hour(col("timestamp"))) \
    .withColumn("latitude", col("location.latitude")) \
    .withColumn("longitude", col("location.longitude")) \
    .withColumn("ingestion_time", current_timestamp())

console_sink = processed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime="5 seconds") \
    .start()

def write_to_hdfs_bronze(batch_df, batch_id):
    batch_df.write \
        .mode("append") \
        .partitionBy("incident_date") \
        .parquet(f"/user/hive/warehouse/bronze/emergency_calls/batch_{batch_id}")

bronze_sink = processed_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_hdfs_bronze) \
    .trigger(processingTime="10 seconds") \
    .start()

def write_to_clickhouse(batch_df, batch_id):
    try:
        if batch_df.count() > 0:
            clickhouse_df = batch_df.select(
                col("call_id").alias("incident_id"),
                col("incident_date"),
                col("incident_type"),
                col("precinct").alias("location_zip"),
                col("latitude"),
                col("longitude"),
                lit(1).alias("incident_count"),
                lit(0).alias("avg_response_time")
            )
            
            clickhouse_df.write \
                .format("jdbc") \
                .option("url", "jdbc:clickhouse://clickhouse:8123/public_safety") \
                .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
                .option("user", "clickhouse") \
                .option("password", "clickhouse") \
                .option("dbtable", "fact_incidents") \
                .mode("append") \
                .save()
            print(f" Batch {batch_id} written to ClickHouse")
    except Exception as e:
        print(f" ClickHouse write failed: {e}")

clickhouse_sink = processed_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_clickhouse) \
    .trigger(processingTime="10 seconds") \
    .start()

print(" All sinks started!")
print("=" * 50)
print(" Streaming Pipeline Running:")
print("   Console output")
print("   HDFS Bronze layer")
print("   ClickHouse analytics")
print("=" * 50)

spark.streams.awaitAnyTermination()