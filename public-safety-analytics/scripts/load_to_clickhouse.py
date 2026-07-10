import clickhouse_connect
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_clickhouse(client, max_retries=30):
    for i in range(max_retries):
        try:
            client.ping()
            logger.info(" Successfully connected to ClickHouse.")
            return
        except Exception as e:
            logger.warning(f"ClickHouse not ready yet, retrying in 2 seconds... ({i+1}/{max_retries})")
            time.sleep(2)
    raise Exception(" Could not connect to ClickHouse after multiple retries.")

def main():
    logger.info(" Connecting to ClickHouse...")
    client = clickhouse_connect.get_client(
        host='clickhouse', 
        port=8123, 
        username='clickhouse', 
        password='clickhouse'
    )
    
    wait_for_clickhouse(client)

    
    client.command("CREATE DATABASE IF NOT EXISTS public_safety")
    
    logger.info(" Truncating tables to remove old data...")
    client.command("TRUNCATE TABLE IF EXISTS public_safety.fact_incidents")
    client.command("TRUNCATE TABLE IF EXISTS public_safety.dim_incident_type")
    client.command("TRUNCATE TABLE IF EXISTS public_safety.dim_location")

    logger.info(" Loading dim_incident_type from HDFS...")
    client.command("""
        INSERT INTO public_safety.dim_incident_type (type_id, type_name, category)
        SELECT type_id, type_name, category
        FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/dim_incident_type.parquet/*.parquet', 'Parquet')
    """)

    logger.info(" Loading dim_location from HDFS...")
    client.command("""
        INSERT INTO public_safety.dim_location (location_id, city)
        SELECT location_id, city
        FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/dim_location.parquet/*.parquet', 'Parquet')
    """)

    logger.info(" Loading fact_incidents from HDFS...")
    client.command("""
        INSERT INTO public_safety.fact_incidents (incident_id, incident_date, type_id, location_id, latitude, longitude)
        SELECT incident_id, incident_date, type_id, location_id, latitude, longitude
        FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/fact_incidents.parquet/*.parquet', 'Parquet')
    """)

    logger.info(" All Star Schema data loaded successfully into ClickHouse from HDFS!")

if __name__ == "__main__":
    main()
