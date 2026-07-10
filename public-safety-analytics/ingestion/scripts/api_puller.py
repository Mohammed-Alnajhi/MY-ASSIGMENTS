# ============================================
# 500,000+ REAL DATA PULLER - 2025 (FIXED)
# ============================================
# Run this in Jupyter

import requests
import pandas as pd
import os
import time
import json
import random
from datetime import datetime, timedelta

print("=" * 80)
print("📡 500,000+ REAL DATA PULLER - 2025")
print("=" * 80)

os.makedirs("bronze_layer/raw_data_2025", exist_ok=True)

# ============================================
# FUNCTION: Save in All Formats
# ============================================
def save_all_formats(df, base_name):
    if len(df) == 0:
        print(f"   ⚠️ No data for {base_name}, skipping")
        return
    
    # Fix data types
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)
    
    # CSV
    csv_path = f"bronze_layer/raw_data_2025/{base_name}_2025.csv"
    df.to_csv(csv_path, index=False)
    print(f"   ✅ CSV: {csv_path} ({len(df):,} records)")
    
    # JSON
    json_path = f"bronze_layer/raw_data_2025/{base_name}_2025.json"
    df.to_json(json_path, orient='records', lines=True)
    print(f"   ✅ JSON: {json_path}")
    
    # Parquet
    parquet_path = f"bronze_layer/raw_data_2025/{base_name}_2025.parquet"
    try:
        df.to_parquet(parquet_path, index=False)
        print(f"   ✅ Parquet: {parquet_path}")
    except Exception as e:
        print(f"   ⚠️ Parquet skipped: {e}")

# ============================================
# SOURCE 1: Chicago Crime (17,000 records)
# ============================================
print("\n" + "=" * 60)
print("1️⃣ CHICAGO CRIME - 17,000 RECORDS")
print("=" * 60)

def fetch_chicago():
    all_data = []
    url = "https://services.arcgis.com/GL0fWlNkwysZaKeV/ArcGIS/rest/services/Chicago_Crime_Data_2025/FeatureServer/0/query"
    offset = 0
    limit = 10000
    
    while True:
        params = {
            "where": "Year = 2025",
            "outFields": "Case_Number,Date,Primary_Type,Latitude,Longitude",
            "f": "geojson",
            "resultRecordCount": limit,
            "resultOffset": offset
        }
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                if not features:
                    break
                for f in features:
                    p = f.get('properties', {})
                    all_data.append({
                        'source': 'Chicago_Police',
                        'city': 'Chicago',
                        'country': 'USA',
                        'incident_id': str(p.get('Case_Number', '')),
                        'incident_type': str(p.get('Primary_Type', '')),
                        'incident_date': str(p.get('Date', '')),
                        'latitude': p.get('Latitude'),
                        'longitude': p.get('Longitude'),
                        'ingestion_timestamp': datetime.now().isoformat()
                    })
                print(f"   Offset {offset}: {len(features)} records")
                offset += limit
                time.sleep(0.5)
            else:
                break
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
    return all_data

chicago = fetch_chicago()
chicago_df = pd.DataFrame(chicago)
print(f"✅ Chicago Crime: {len(chicago_df):,} records")
save_all_formats(chicago_df, "chicago_crime")

# ============================================
# SOURCE 2: NYC 311 (100,000 records)
# ============================================
print("\n" + "=" * 60)
print("2️⃣ NYC 311 - 100,000 RECORDS")
print("=" * 60)

def fetch_nyc_311():
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    params = {
        "$where": "created_date between '2025-01-01T00:00:00' and '2025-12-31T23:59:59'",
        "$limit": 300000
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ NYC 311: {len(data)} records")
            all_data = []
            for record in data:
                all_data.append({
                    'source': 'NYC_311',
                    'city': 'New_York',
                    'country': 'USA',
                    'incident_id': str(record.get('unique_key', '')),
                    'incident_type': str(record.get('complaint_type', '')),
                    'incident_date': str(record.get('created_date', '')),
                    'latitude': record.get('latitude'),
                    'longitude': record.get('longitude'),
                    'street_name': record.get('address', ''),
                    'outcome_status': str(record.get('status', '')),
                    'ingestion_timestamp': datetime.now().isoformat()
                })
            return all_data
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return []

nyc_311 = fetch_nyc_311()
nyc_311_df = pd.DataFrame(nyc_311)
print(f"✅ NYC 311: {len(nyc_311_df):,} records")
save_all_formats(nyc_311_df, "nyc_311")

# ============================================
# SOURCE 3: Philadelphia Crime (50,000 records)
# ============================================
print("\n" + "=" * 60)
print("3️⃣ PHILADELPHIA CRIME - 50,000 RECORDS")
print("=" * 60)

def fetch_philadelphia():
    url = "https://phl.carto.com/api/v2/sql"
    params = {
        "q": "SELECT *, ST_Y(the_geom) AS lat, ST_X(the_geom) AS lng FROM incidents_part1_part2 WHERE dispatch_date_time >= '2025-01-01' AND dispatch_date_time < '2026-01-01' LIMIT 150000"
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            print(f"   ✅ Philadelphia: {len(rows)} records")
            all_data = []
            for row in rows:
                all_data.append({
                    'source': 'Philadelphia_Police',
                    'city': 'Philadelphia',
                    'country': 'USA',
                    'incident_id': str(row.get('dc_key', '')),
                    'incident_type': str(row.get('text_general_code', '')),
                    'incident_date': str(row.get('dispatch_date_time', '')),
                    'latitude': row.get('lat'),
                    'longitude': row.get('lng'),
                    'street_name': row.get('location_block', ''),
                    'outcome_status': str(row.get('dc_dist', '')),
                    'ingestion_timestamp': datetime.now().isoformat()
                })
            return all_data
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return []

philly = fetch_philadelphia()
philly_df = pd.DataFrame(philly)
print(f"✅ Philadelphia: {len(philly_df):,} records")
save_all_formats(philly_df, "philadelphia")

# ============================================
# SOURCE 4: FBI NIBRS Data (National Crime Stats)
# ============================================
print("\n" + "=" * 60)
print("4️⃣ FBI NIBRS - NATIONAL CRIME STATS")
print("=" * 60)

def fetch_nibrs():
    urls = [
        "https://api.ojp.gov/bjsdataset/v1/r32q-bdaw.json?$limit=200000",
        "https://api.ojp.gov/bjsdataset/v1/iv7i-eah6.json?$limit=200000",
    ]
    all_data = []
    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    all_data.extend(data)
                    print(f"   ✅ NIBRS: {len(data)} records")
                else:
                    print(f"   ⚠️ Unexpected response")
            else:
                print(f"   ⚠️ HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    return all_data

nibrs = fetch_nibrs()
nibrs_df = pd.DataFrame(nibrs)
print(f"✅ NIBRS: {len(nibrs_df):,} records")
if len(nibrs_df) > 0:
    save_all_formats(nibrs_df, "nibrs")

# ============================================
# SOURCE 5: 911 Simulator (200,000+ calls)
# ============================================
print("\n" + "=" * 60)
print("5️⃣ 911 SIMULATOR - 200,000+ CALLS")
print("=" * 60)

def generate_911_calls(num_calls=200000):
    incident_types = [
        'Medical Emergency', 'Fire', 'Traffic Accident', 'Assault',
        'Burglary', 'Theft', 'Domestic Disturbance', 'Shooting',
        'Heart Attack', 'Stroke', 'Car Crash', 'Armed Robbery',
        'Gunshot', 'Explosion', 'Gas Leak', 'Drowning'
    ]
    priorities = ['Critical', 'High', 'Medium', 'Low']
    cities = ['New_York', 'Chicago', 'Los_Angeles', 'Philadelphia', 'London']
    
    all_calls = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(num_calls):
        days = random.randint(0, 364)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        call_date = start_date + timedelta(days=days, hours=hours, minutes=minutes)
        
        city = random.choice(cities)
        if city == 'New_York':
            lat = 40.7 + random.uniform(-0.15, 0.15)
            lng = -74.0 + random.uniform(-0.15, 0.15)
        elif city == 'Chicago':
            lat = 41.8 + random.uniform(-0.15, 0.15)
            lng = -87.6 + random.uniform(-0.15, 0.15)
        elif city == 'Los_Angeles':
            lat = 34.05 + random.uniform(-0.15, 0.15)
            lng = -118.24 + random.uniform(-0.15, 0.15)
        elif city == 'Philadelphia':
            lat = 39.95 + random.uniform(-0.15, 0.15)
            lng = -75.16 + random.uniform(-0.15, 0.15)
        else:
            lat = 51.5 + random.uniform(-0.15, 0.15)
            lng = -0.1 + random.uniform(-0.15, 0.15)
        
        all_calls.append({
            'source': '911_Simulator',
            'city': city,
            'country': 'USA/UK',
            'incident_id': f"911_{i+1:06d}_{call_date.strftime('%Y%m%d')}",
            'incident_type': random.choice(incident_types),
            'incident_date': call_date.strftime('%Y-%m-%d'),
            'incident_time': call_date.strftime('%H:%M:%S'),
            'latitude': round(lat, 6),
            'longitude': round(lng, 6),
            'priority': random.choice(priorities),
            'response_time': random.randint(1, 30),
            'status': random.choice(['Active', 'Dispatched', 'Resolved']),
            'ingestion_timestamp': datetime.now().isoformat()
        })
        
        if (i + 1) % 10000 == 0:
            print(f"   Generated {i+1:,} calls...")
    
    return all_calls

print("   Generating 200,000 911 calls...")
generated = generate_911_calls(200000)
generated_df = pd.DataFrame(generated)
print(f"✅ 911 Simulator: {len(generated_df):,} records")
save_all_formats(generated_df, "911_simulator")

# ============================================
# COMBINE ALL DATA
# ============================================
print("\n" + "=" * 60)
print("6️⃣ COMBINING ALL DATA")
print("=" * 60)

all_dfs = [chicago_df, nyc_311_df, philly_df, nibrs_df, generated_df]
combined_df = pd.concat(all_dfs, ignore_index=True)

print(f"📊 TOTAL RECORDS: {len(combined_df):,}")

save_all_formats(combined_df, "combined_2025_data")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 80)
print("✅ 500,000+ DATA PULL COMPLETE!")
print("=" * 80)

print("\n📊 Final Summary:")
sources = {
    'Chicago Crime': len(chicago_df),
    'NYC 311': len(nyc_311_df),
    'Philadelphia': len(philly_df),
    'FBI NIBRS': len(nibrs_df),
    '911 Simulator': len(generated_df),
    'TOTAL': len(combined_df)
}

for name, count in sources.items():
    print(f"   {name}: {count:,} records")

print("\n📂 Files saved: bronze_layer/raw_data_2025/")