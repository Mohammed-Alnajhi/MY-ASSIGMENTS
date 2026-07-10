CREATE DATABASE IF NOT EXISTS public_safety;

DROP TABLE IF EXISTS public_safety.dim_incident_type;
CREATE TABLE IF NOT EXISTS public_safety.dim_incident_type (
    type_id Int64,
    type_name String,
    category String
) ENGINE = MergeTree()
ORDER BY type_id;

DROP TABLE IF EXISTS public_safety.dim_location;
CREATE TABLE IF NOT EXISTS public_safety.dim_location (
    location_id Int64,
    city String
) ENGINE = MergeTree()
ORDER BY location_id;

DROP TABLE IF EXISTS public_safety.fact_incidents;
CREATE TABLE IF NOT EXISTS public_safety.fact_incidents (
    incident_id String,
    incident_date Date,
    type_id Int64,
    location_id Int64,
    latitude Float64,
    longitude Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(incident_date)
ORDER BY (incident_date, location_id, type_id)
SETTINGS index_granularity = 8192;

TRUNCATE TABLE IF EXISTS public_safety.fact_incidents;
TRUNCATE TABLE IF EXISTS public_safety.dim_incident_type;
TRUNCATE TABLE IF EXISTS public_safety.dim_location;

INSERT INTO public_safety.dim_incident_type (type_id, type_name, category)
SELECT type_id, type_name, category
FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/dim_incident_type.parquet/*.parquet', 'Parquet');

INSERT INTO public_safety.dim_location (location_id, city)
SELECT location_id, city
FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/dim_location.parquet/*.parquet', 'Parquet');

INSERT INTO public_safety.fact_incidents (incident_id, incident_date, type_id, location_id, latitude, longitude)
SELECT incident_id, incident_date, type_id, location_id, latitude, longitude
FROM hdfs('hdfs://namenode:9000/user/hive/warehouse/gold/fact_incidents.parquet/*.parquet', 'Parquet');
