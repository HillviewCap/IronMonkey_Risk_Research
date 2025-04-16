-- Create global_cybersecurity_threats_eda table for tracking cybersecurity incidents
CREATE TABLE IF NOT EXISTS global_cybersecurity_threats_eda (
id SERIAL PRIMARY KEY,
country TEXT NOT NULL,
year INTEGER NOT NULL,
threat_type TEXT NOT NULL,
attack_vector TEXT NOT NULL,
affected_industry TEXT NOT NULL,
data_breached_gb DOUBLE PRECISION,
financial_impact_m DOUBLE PRECISION,
severity_level TEXT NOT NULL,
response_time_hours DOUBLE PRECISION,
mitigation_strategy TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for commonly queried columns
CREATE INDEX IF NOT EXISTS idx_cybersecurity_threats_country ON global_cybersecurity_threats_eda(country);
CREATE INDEX IF NOT EXISTS idx_cybersecurity_threats_year ON global_cybersecurity_threats_eda(year);
CREATE INDEX IF NOT EXISTS idx_cybersecurity_threats_type ON global_cybersecurity_threats_eda(threat_type);
CREATE INDEX IF NOT EXISTS idx_cybersecurity_threats_industry ON global_cybersecurity_threats_eda(affected_industry);
