-- Raw data directly ingested from external sources
CREATE SCHEMA IF NOT EXISTS raw;

-- Cleaned and standardized intermediate data
CREATE SCHEMA IF NOT EXISTS staging;

-- Trusted business entities
CREATE SCHEMA IF NOT EXISTS core;

-- Analytical views and aggregated datasets
CREATE SCHEMA IF NOT EXISTS analytics;