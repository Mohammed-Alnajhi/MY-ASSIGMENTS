CREATE DATABASE IF NOT EXISTS public_safety;

CREATE TABLE IF NOT EXISTS public_safety.dim_incident_type (
    type_id Int64,
    type_name String,
    category String
) ENGINE = MergeTree()
ORDER BY type_id;

CREATE TABLE IF NOT EXISTS public_safety.dim_location (
    location_id Int64,
    city String
) ENGINE = MergeTree()
ORDER BY location_id;

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

CREATE VIEW IF NOT EXISTS public_safety.dashboard_view AS
SELECT 
    f.incident_id,
    f.incident_date,
    t.type_name,
    t.category as source,
    l.city,
    f.latitude,
    f.longitude
FROM public_safety.fact_incidents f
LEFT JOIN public_safety.dim_incident_type t ON f.type_id = t.type_id
LEFT JOIN public_safety.dim_location l ON f.location_id = l.location_id;