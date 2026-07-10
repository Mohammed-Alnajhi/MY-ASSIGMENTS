import requests
import pandas as pd
import os

def ch_query(query):
    try:
        response = requests.post(
            'http://clickhouse:8123/',
            params={'query': query},
            auth=('clickhouse', 'clickhouse'),
            timeout=120
        )
        return response.status_code == 200
    except Exception as e:
        print(f" Error: {e}")
        return False

print(" Loading Gold data to ClickHouse...")

files = {
    'fact_incidents': 'gold_layer/fact_incidents.csv',
    'dim_incident_type': 'gold_layer/dim_incident_type.csv',
    'agg_hourly_trends': 'gold_layer/agg_hourly_trends.csv',
    'agg_location': 'gold_layer/agg_location.csv'
}

for table_name, file_path in files.items():
    if not os.path.exists(file_path):
        print(f" {file_path} not found")
        continue
    
    df = pd.read_csv(file_path)
    print(f" Loading {table_name}: {len(df)} records")
    
    for _, row in df.iterrows():
        if table_name == 'fact_incidents':
            query = f"""
            INSERT INTO public_safety.fact_incidents VALUES (
                '{row['incident_date']}','{row['incident_type']}','{row['source']}',
                {row['incident_count']},{row['avg_latitude']},{row['avg_longitude']},
                {row['year']},{row['month']}
            )
            """
        elif table_name == 'dim_incident_type':
            query = f"""
            INSERT INTO public_safety.dim_incident_type VALUES (
                {row['type_id']},'{row['incident_type']}','{row['category']}'
            )
            """
        elif table_name == 'agg_hourly_trends':
            query = f"""
            INSERT INTO public_safety.agg_hourly_trends VALUES (
                '{row['incident_date']}',{row['hour']},'{row['incident_type']}',{row['incident_count']}
            )
            """
        elif table_name == 'agg_location':
            query = f"""
            INSERT INTO public_safety.agg_location VALUES (
                '{row['source']}',{row['total_incidents']},
                {row['avg_latitude']},{row['avg_longitude']},
                {row['min_latitude']},{row['max_latitude']},
                {row['min_longitude']},{row['max_longitude']}
            )
            """
        ch_query(query)
    
    print(f" Loaded {table_name}")

print(" All data loaded to ClickHouse!")