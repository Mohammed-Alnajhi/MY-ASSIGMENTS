# Data Dictionary: Public Safety Analytics

## Fact Table: fact_incidents (Batch Historical Data)
| Column | Type | Description |
|--------|------|-------------|
| incident_id | String | Unique incident identifier |
| incident_date | Date | Date of the incident |
| type_id | Int64 | Reference to the incident type dimension |
| location_id | Int64 | Reference to the location dimension |
| latitude | Float64 | Geographic latitude of the incident |
| longitude | Float64 | Geographic longitude of the incident |

## Dimension Table: dim_location
| Column | Type | Description |
|--------|------|-------------|
| location_id | Int64 | Unique key of location |
| city | String | Name of the city |

## Dimension Table: dim_incident_type
| Column | Type | Description |
|--------|------|-------------|
| type_id | Int64 | Unique key of incident type |
| type_name | String | Name/description of incident |
| category | String | Broader crime grouping |

## Real-time Table: emergency_calls_live (Live Ingestion Data)
| Column | Type | Description |
|--------|------|-------------|
| incident_id | String | Unique live incident identifier |
| incident_date | Date | Date of the incoming call |
| incident_type | String | Specific type of emergency |
| location_zip | String | Zip code/Precinct identifier |
| latitude | Float64 | Call location latitude |
| longitude | Float64 | Call location longitude |
| incident_count | Int32 | Constant counter (value = 1) |
| avg_response_time | Int32 | Average response time (value = 0) |