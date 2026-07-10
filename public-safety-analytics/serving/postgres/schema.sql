CREATE TABLE IF NOT EXISTS emergency_calls_live (
    call_id VARCHAR(50) PRIMARY KEY,
    incident_type VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    priority VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    police_unit_assigned VARCHAR(20),
    precinct VARCHAR(50)
);

CREATE INDEX idx_timestamp ON emergency_calls_live(timestamp DESC);
CREATE INDEX idx_location ON emergency_calls_live(latitude, longitude);
CREATE INDEX idx_status ON emergency_calls_live(status);
CREATE INDEX idx_type ON emergency_calls_live(incident_type);

CREATE TABLE IF NOT EXISTS realtime_incident_counts (
    incident_type VARCHAR(100),
    count_5min INTEGER,
    count_1hour INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (incident_type, timestamp)
);

CREATE TABLE IF NOT EXISTS alerts_live (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_alerts_unacknowledged ON alerts_live(acknowledged) WHERE acknowledged = FALSE;