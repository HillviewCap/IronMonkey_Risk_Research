-- Create global_countries_eda table based on Kaggle dataset
CREATE TABLE IF NOT EXISTS global_countries_eda (
id SERIAL PRIMARY KEY,
country VARCHAR(100) NOT NULL,
density_per_km2 FLOAT,
abbreviation VARCHAR(10),
agricultural_land_percent FLOAT,
land_area_km2 FLOAT,
armed_forces_size FLOAT,
birth_rate FLOAT,
calling_code VARCHAR(20),
capital_city VARCHAR(100),
co2_emissions FLOAT,
cpi FLOAT,
cpi_change_percent FLOAT,
currency_code VARCHAR(10),
fertility_rate FLOAT,
forested_area_percent FLOAT,
gasoline_price FLOAT,
gdp FLOAT,
primary_education_enrollment_percent FLOAT,
tertiary_education_enrollment_percent FLOAT,
infant_mortality FLOAT,
largest_city VARCHAR(100),
life_expectancy FLOAT,
maternal_mortality_ratio FLOAT,
minimum_wage FLOAT,
official_language VARCHAR(100),
out_of_pocket_health_expenditure FLOAT,
physicians_per_thousand FLOAT,
population FLOAT,
labor_force_participation_percent FLOAT,
tax_revenue_percent FLOAT,
total_tax_rate FLOAT,
unemployment_rate FLOAT,
urban_population FLOAT,
latitude FLOAT,
longitude FLOAT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for commonly queried columns
CREATE INDEX IF NOT EXISTS idx_global_countries_country ON global_countries_eda(country);
CREATE INDEX IF NOT EXISTS idx_global_countries_region ON global_countries_eda(abbreviation);
CREATE INDEX IF NOT EXISTS idx_global_countries_population ON global_countries_eda(population);
