# Technology Stack Justification

## Ingestion Layer
### Apache Kafka (Real-time)
- Industry standard for streaming
- High throughput (millions/sec)
- Exactly-once semantics
- Durable persistence
- **3 Partitions**: Configured on the topic to support partition-based concurrency and scalability.

## Processing Layer
### Apache Spark (Batch + Stream)
- Distributed processing for scale
- Unified batch and streaming API
- In-memory computation
- MLlib for machine learning
- **Python Integration (`clickhouse-connect`)**: Refactored the streaming write layer from JVM JDBC to python-native `clickhouse-connect`. This completely bypasses Maven package resolution issues and proxy/DNS blocks on the Spark cluster, while allowing extremely robust, lightweight data insertions.

## Orchestration
### Apache Airflow
- Rich UI for monitoring
- Dynamic DAG generation
- 1000+ operators
- Backfilling support
- **Docker Integration**: Configured to safely run Spark batch scripts within other containers while correctly checking container exit codes.

## Storage Layer
### HDFS (Data Lake)
- Unlimited scale
- Cost-effective
- Integration with Hadoop ecosystem
- Parquet/ORC support

### ClickHouse (Analytics DB)
- Fast OLAP queries
- Columnar storage
- Real-time ingestion
- SQL support

## Infrastructure
### Docker Compose
- Consistent development environment
- Easy deployment
- Service isolation
- Health checks
- **Volume Bindings**: Configured on the dashboard container (`streamlit-dashboard`) to allow instant live-reloading of interface code changes without requiring container rebuilds.