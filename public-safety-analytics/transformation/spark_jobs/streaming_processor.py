from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

print("=" * 60)
print(" Spark Streaming - Kafka to ClickHouse")
print("=" * 60)

spark = SparkSession.builder \
    .appName("KafkaToClickHouse") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

print(" Spark session created")

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


print("\n Reading from Kafka...")

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "emergency_calls") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", 100) \
    .load()

print(" Connected to Kafka")

parsed_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", schema).alias("data")) \
    .select("data.*") \
    .withColumn("incident_date", to_date("timestamp")) \
    .withColumn("incident_hour", hour("timestamp")) \
    .withColumn("latitude", col("location.latitude")) \
    .withColumn("longitude", col("location.longitude")) \
    .withColumn("ingestion_time", current_timestamp())

print(" Parsed JSON")

console_query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime="5 seconds") \
    .start()

print(" Console sink started")


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
            
            import clickhouse_connect
            client = clickhouse_connect.get_client(
                host="clickhouse",
                port=8123,
                username="clickhouse",
                password="clickhouse",
                database="public_safety"
            )
            pandas_df = clickhouse_df.toPandas()
            client.insert_df("emergency_calls_live", pandas_df)
            
            print(f" Batch {batch_id}: {batch_df.count()} records to ClickHouse")
    except Exception as e:
        print(f" ClickHouse write failed: {e}")

clickhouse_query = parsed_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_clickhouse) \
    .trigger(processingTime="10 seconds") \
    .start()

print(" ClickHouse sink started")
print("\n" + "=" * 60)
print(" Streaming is running!")
print("   Check Spark UI: http://localhost:8081")
print("   Press Ctrl+C to stop")
print("=" * 60)

spark.streams.awaitAnyTermination()