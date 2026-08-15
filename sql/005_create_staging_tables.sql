-- ============================================================
-- Global Flight Data Pipeline
-- Staging layer tables
--
-- Purpose:
--   Store cleaned and standardized versions of the raw
--   OurAirports datasets before loading them into the core layer.
--
-- Notes:
--   - Primary keys are validated against the raw datasets.
--   - Business identifiers validated as unique are constrained.
--   - Foreign keys are intentionally not enforced in staging.
--   - Data lineage columns from raw are preserved.
-- ============================================================


-- ============================================================
-- Airports
-- ============================================================

CREATE TABLE staging.airports (
    id BIGINT PRIMARY KEY,

    ident TEXT NOT NULL,
    type TEXT,
    name TEXT,

    latitude_deg DOUBLE PRECISION,
    longitude_deg DOUBLE PRECISION,
    elevation_ft INTEGER,

    continent TEXT,
    iso_country TEXT,
    iso_region TEXT,
    municipality TEXT,

    scheduled_service BOOLEAN,

    gps_code TEXT,
    icao_code TEXT,
    iata_code TEXT,
    local_code TEXT,

    home_link TEXT,
    wikipedia_link TEXT,
    keywords TEXT,

    ingested_at TIMESTAMPTZ NOT NULL,
    source_file TEXT,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_staging_airports_ident UNIQUE (ident)
);


-- ============================================================
-- Countries
-- ============================================================

CREATE TABLE staging.countries (
    id BIGINT PRIMARY KEY,

    code TEXT NOT NULL,
    name TEXT,
    continent TEXT,

    wikipedia_link TEXT,
    keywords TEXT,

    ingested_at TIMESTAMPTZ NOT NULL,
    source_file TEXT,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_staging_countries_code UNIQUE (code)
);


-- ============================================================
-- Regions
-- ============================================================

CREATE TABLE staging.regions (
    id BIGINT PRIMARY KEY,

    code TEXT NOT NULL,
    local_code TEXT,
    name TEXT,

    continent TEXT,
    iso_country TEXT,

    wikipedia_link TEXT,
    keywords TEXT,

    ingested_at TIMESTAMPTZ NOT NULL,
    source_file TEXT,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_staging_regions_code UNIQUE (code)
);


-- ============================================================
-- Runways
-- ============================================================

CREATE TABLE staging.runways (
    id BIGINT PRIMARY KEY,

    airport_ref BIGINT,
    airport_ident TEXT,

    length_ft DOUBLE PRECISION,
    width_ft DOUBLE PRECISION,
    surface TEXT,

    lighted BOOLEAN,
    closed BOOLEAN,

    le_ident TEXT,
    le_latitude_deg DOUBLE PRECISION,
    le_longitude_deg DOUBLE PRECISION,
    le_elevation_ft DOUBLE PRECISION,
    le_heading_degt DOUBLE PRECISION,
    le_displaced_threshold_ft DOUBLE PRECISION,

    he_ident TEXT,
    he_latitude_deg DOUBLE PRECISION,
    he_longitude_deg DOUBLE PRECISION,
    he_elevation_ft DOUBLE PRECISION,
    he_heading_degt DOUBLE PRECISION,
    he_displaced_threshold_ft DOUBLE PRECISION,

    ingested_at TIMESTAMPTZ NOT NULL,
    source_file TEXT,
    staged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);