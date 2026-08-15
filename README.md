# Global Flight Data Pipeline

## Overview

Global Flight Data Pipeline is a Data Engineering project designed to build an end-to-end data pipeline for ingesting, storing, transforming, validating, and analyzing global flight data.

The project will progressively include:

* Flight data ingestion from APIs and datasets
* Raw data storage
* Data cleaning and transformation
* PostgreSQL data modeling
* ETL / ELT pipelines
* Apache Airflow orchestration
* Scheduling and retry mechanisms
* Logging and error handling
* Data quality checks
* Analytical SQL queries
* Automated tests
* Monitoring
* CI/CD
* Deployment

## Project Status

🚧 **In Progress — Raw Ingestion, Staging Transformation & Data Quality**

### Completed

* Project structure and local Python environment setup
* Docker and Docker Compose configuration
* PostgreSQL 17 database setup
* Database schemas created:

  * `raw`
  * `staging`
  * `core`
  * `analytics`
* OurAirports datasets downloaded and integrated:

  * Airports
  * Countries
  * Regions
  * Runways
* Raw PostgreSQL tables created
* Python ingestion pipeline implemented
* CSV validation before ingestion
* Bulk loading into PostgreSQL using `COPY`
* Logging and ingestion error handling
* Raw data integrity checks
* Raw → Staging transformation implemented
* Data cleaning and standardization in the staging layer
* Raw / staging row-count validation
* Initial data quality framework with:

  * Failure checks
  * Warning checks

### Current Work

* Expanding staging-layer data quality checks
* Validating cleaned and standardized datasets
* Preparing the transition from `staging` to the `core` data model

### Next Steps

* Design and implement the `core` data model
* Create relationships and constraints between core entities
* Transform staging data into core tables
* Add more advanced data quality checks
* Implement automated tests
* Introduce Apache Airflow orchestration
* Add scheduling, retries, and monitoring
* Build the analytical layer
* Prepare CI/CD and deployment
