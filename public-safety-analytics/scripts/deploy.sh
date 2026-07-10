#!/bin/bash

echo "🚀 Starting deployment of Public Safety Incident Analysis Pipeline..."

# 1. Set up environment
echo "📦 Setting up environment..."
cp .env.example .env 2>/dev/null || true

# 2. Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# 3. Wait for services
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

# 4. Create Kafka topics
echo "📨 Creating Kafka topics..."
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
    --create \
    --bootstrap-server localhost:9092 \
    --topic emergency_calls \
    --partitions 3 \
    --replication-factor 1 2>/dev/null || echo "Topic may already exist"

# 5. Create HDFS directories
echo "💾 Creating HDFS directories..."
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse/bronze/crime_api 2>/dev/null
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse/bronze/incident_reports 2>/dev/null
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse/bronze/emergency_calls 2>/dev/null
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse/silver/incidents 2>/dev/null
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse/gold/fact_incidents 2>/dev/null
docker exec namenode hdfs dfs -chmod -R 777 /user/hive/warehouse 2>/dev/null

# 6. Initialize ClickHouse
echo "🔷 Initializing ClickHouse..."
docker exec clickhouse clickhouse-client --user clickhouse --password clickhouse \
    --query "CREATE DATABASE IF NOT EXISTS public_safety"

# 7. Initialize PostgreSQL
echo "🐘 Initializing PostgreSQL..."
docker exec postgres-realtime psql -U safety_user -d public_safety_realtime \
    -c "CREATE TABLE IF NOT EXISTS emergency_calls_live (call_id VARCHAR(50) PRIMARY KEY, incident_type VARCHAR(100), latitude DECIMAL(10,8), longitude DECIMAL(11,8), timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, priority VARCHAR(20), status VARCHAR(20) DEFAULT 'active')"

# 8. Start NiFi flow (via API)
echo "🔄 Starting NiFi flow..."

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Access URLs:"
echo "  Airflow:  http://localhost:8085  (admin/admin)"
echo "  Spark:    http://localhost:8081"
echo "  Kafka UI: http://localhost:8090"
echo "  NiFi:     https://localhost:8443 (admin/SuperSecretPassword123!)"
echo "  Jupyter:  http://localhost:8888"
echo "  HDFS:     http://localhost:9870"
echo "  ClickHouse: http://localhost:8123"