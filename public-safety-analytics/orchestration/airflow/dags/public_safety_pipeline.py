from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1),
    'email_on_failure': [],
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'catchup': False
}


dag = DAG(
    'public_safety_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline for public safety incidents',
    schedule_interval='0 2 * * *',  
    max_active_runs=1,
    tags=['public_safety', 'etl']
)




start = DummyOperator(task_id='start', dag=dag)


check_kafka = BashOperator(
    task_id='check_kafka',
    bash_command='''
        echo " Kafka is running"
        docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
    ''',
    dag=dag
)


silver_transform = BashOperator(
    task_id='silver_transformation',
    bash_command='''
        echo "🧹 Running Silver Transformation..."
        docker exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/silver_transformation.py
    ''',
    dag=dag
)


gold_aggregation = BashOperator(
    task_id='gold_aggregation',
    bash_command='''
        echo " Running Gold Aggregation..."
        docker exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/gold_aggregation.py
    ''',
    dag=dag
)


load_clickhouse = BashOperator(
    task_id='load_to_clickhouse',
    bash_command='''
        echo "📤 Loading to ClickHouse..."
        python /opt/airflow/scripts/load_to_clickhouse.py
    ''',
    dag=dag
)


end = DummyOperator(task_id='end', dag=dag)


start >> check_kafka
check_kafka >> silver_transform
silver_transform >> gold_aggregation
gold_aggregation >> load_clickhouse
load_clickhouse >> end