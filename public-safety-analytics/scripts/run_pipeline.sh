echo " Running Public Safety Pipeline..."


echo "1️ Generating test data..."
python ingestion/kafka/producers/emergency_call_simulator.py &
echo "2️ Starting Spark streaming..."
docker exec spark-master spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /opt/spark/jobs/streaming_processor.py &
SPARK_PID=$!

echo " Pipeline running. Press Ctrl+C to stop."
wait $SIMULATOR_PID $SPARK_PID