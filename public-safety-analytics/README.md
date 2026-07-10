# 🚨 Public Safety Analytics Command Center

Welcome to the Public Safety Analytics project! This platform implements a real-time and batch data engineering pipeline to ingest, process, and visualize emergency call and crime data across global cities.

---

## 🏗 System Architecture

The pipeline uses a **Lambda Architecture** that processes both real-time streams and daily batch logs:

- **Ingestion**: Apache Kafka (3-partition real-time emergency call simulator)
- **Processing**: Apache Spark (Structured Streaming with `clickhouse-connect` native ingestion & Batch processing)
- **Storage**: ClickHouse (OLAP Gold analytics database), HDFS (Bronze/Silver layers)
- **Orchestration**: Apache Airflow (Docker-based pipeline runner)
- **Visualization**: Streamlit Dashboard (Plotly-based SVG interactive maps and charts)

---

## 🚀 How to Start the Project

Follow these steps to spin up the Docker containers, run the pipeline, and view the dashboard:

### 1. Start the Infrastructure
Make sure Docker Desktop is running, then open your terminal in the root directory of this repository and run:
```bash
docker-compose up -d
```
Wait about 2–3 minutes for all containers to reach a `healthy` state. You can verify this by running:
```bash
docker ps
```

### Pull data from ingestion/scripts/api_puller.py

### 2. Start the Streaming Pipeline (via Jupyter)
Instead of using PowerShell scripts, the entire pipeline is orchestrated via Jupyter:
1. Open your browser and navigate to Jupyter Lab: **[http://localhost:8888](http://localhost:8888)**
2. In the file explorer, navigate to `notebooks/` and open **`01_Run_Project.ipynb`**.
3. Run the cells in order:
   - **Cell 1**: Launches the background Kafka Simulator (which pushes simulated 911 calls to the 3-partition `emergency_calls` topic).
   - **Cell 2**: Submits the Spark Streaming Job (`streaming_processor.py`) to the cluster, which consumes from Kafka, maps schemas, and streams records into ClickHouse's live table.
   - *Note: The notebook is self-cleaning and automatically terminates any old running submits to prevent core starvation.*

### 3. Open the Streamlit Dashboard
Once Spark is processing events, open your browser and navigate to:
👉 **[http://localhost:8502](http://localhost:8502)**

The dashboard displays:
- **Total Incidents (Live + Batch union)** with real-time counters.
- **City-wise Top Incident Map**: A robust SVG map displaying London, NYC, Philadelphia, Los Angeles, and Chicago. City circles are sized by crime volume, colored by their primary incident type, and labeled clearly with city names and their specific problems.
- **Grouped Crime Types**: A horizontal bar chart showing categories normalized and grouped correctly.

### 4. Run the Batch ETL Pipeline (via Airflow)
To schedule or run the daily batch aggregates:
1. Navigate to the Airflow Web UI: **[http://localhost:8085](http://localhost:8085)** (Username: `admin` / Password: `admin`).
2. Turn on the **`public_safety_pipeline`** DAG.
3. Trigger a manual execution using the blue play button. It will test Kafka connections, run Silver and Gold Spark batch jobs, and bulk-load data into ClickHouse dimension and fact tables.

### 5. Stopping the Project
To stop the streaming pipeline:
- Run the **Stop Simulator** cell inside the Jupyter notebook to kill the background generator.
- Interrupt the Spark streaming cell in Jupyter (hit the stop button or restart the kernel).
To shut down the docker infrastructure:
```bash
docker-compose down
```

---

## 🛠 Useful Ports & Interfaces

- **Streamlit Dashboard**: `http://localhost:8502`
- **Jupyter Lab**: `http://localhost:8888`
- **Airflow Web UI**: `http://localhost:8085`
- **Spark Master UI**: `http://localhost:8080`
- **Kafka UI**: `http://localhost:8090`
- **ClickHouse HTTP interface**: `http://localhost:8123`
- **Hadoop NameNode**: `http://localhost:9870`
