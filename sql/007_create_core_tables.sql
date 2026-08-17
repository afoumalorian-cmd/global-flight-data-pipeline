-- =============================================================================
-- Migration: 007_create_core_tables.sql
-- Purpose: Create the trusted CORE relational model
-- =============================================================================

BEGIN;

-- =============================================================================
-- COUNTRIES
-- =============================================================================

CREATE TABLE core.countries (
    country_id          BIGINT GENERATED ALWAYS AS IDENTITY,
    source_country_id   BIGINT NOT NULL,
    code                TEXT NOT NULL,
    name                TEXT NOT NULL,
    continent_code      TEXT,
    wikipedia_link      TEXT,
    keywords            TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_core_countries
        PRIMARY KEY (country_id),

    CONSTRAINT uq_core_countries_source
        UNIQUE (source_country_id),

    CONSTRAINT uq_core_countries_code
        UNIQUE (code)
);


-- =============================================================================
-- REGIONS
-- =============================================================================

CREATE TABLE core.regions (
    region_id           BIGINT GENERATED ALWAYS AS IDENTITY,
    source_region_id    BIGINT NOT NULL,
    country_id          BIGINT NOT NULL,
    code                TEXT NOT NULL,
    local_code          TEXT,
    name                TEXT NOT NULL,
    wikipedia_link      TEXT,
    keywords            TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_core_regions
        PRIMARY KEY (region_id),

    CONSTRAINT uq_core_regions_source
        UNIQUE (source_region_id),

    CONSTRAINT uq_core_regions_code
        UNIQUE (code),

    CONSTRAINT fk_core_regions_country
        FOREIGN KEY (country_id)
        REFERENCES core.countries (country_id)
);


-- =============================================================================
-- AIRPORTS
-- =============================================================================

CREATE TABLE core.airports (
    airport_id          BIGINT GENERATED ALWAYS AS IDENTITY,
    source_airport_id   BIGINT NOT NULL,
    region_id           BIGINT NOT NULL,

    ident               TEXT NOT NULL,
    type                TEXT NOT NULL,
    name                TEXT NOT NULL,

    latitude_deg        DOUBLE PRECISION NOT NULL,
    longitude_deg       DOUBLE PRECISION NOT NULL,
    elevation_ft        INTEGER,

    municipality        TEXT,
    scheduled_service   BOOLEAN NOT NULL,

    gps_code            TEXT,
    icao_code           TEXT,
    iata_code           TEXT,
    local_code          TEXT,

    home_link           TEXT,
    wikipedia_link      TEXT,
    keywords            TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_core_airports
        PRIMARY KEY (airport_id),

    CONSTRAINT uq_core_airports_source
        UNIQUE (source_airport_id),

    CONSTRAINT uq_core_airports_ident
        UNIQUE (ident),

    CONSTRAINT fk_core_airports_region
        FOREIGN KEY (region_id)
        REFERENCES core.regions (region_id),

    CONSTRAINT chk_core_airports_latitude
        CHECK (latitude_deg BETWEEN -90 AND 90),

    CONSTRAINT chk_core_airports_longitude
        CHECK (longitude_deg BETWEEN -180 AND 180)
);


-- =============================================================================
-- RUNWAYS
-- =============================================================================

CREATE TABLE core.runways (
    runway_id                   BIGINT GENERATED ALWAYS AS IDENTITY,
    source_runway_id            BIGINT NOT NULL,
    airport_id                  BIGINT NOT NULL,

    length_ft                   INTEGER,
    width_ft                    INTEGER,
    surface                     TEXT,
    lighted                     BOOLEAN NOT NULL,
    closed                      BOOLEAN NOT NULL,

    le_ident                    TEXT,
    le_latitude_deg             DOUBLE PRECISION,
    le_longitude_deg            DOUBLE PRECISION,
    le_elevation_ft             INTEGER,
    le_heading_degt             DOUBLE PRECISION,
    le_displaced_threshold_ft   INTEGER,

    he_ident                    TEXT,
    he_latitude_deg             DOUBLE PRECISION,
    he_longitude_deg            DOUBLE PRECISION,
    he_elevation_ft             INTEGER,
    he_heading_degt             DOUBLE PRECISION,
    he_displaced_threshold_ft   INTEGER,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_core_runways
        PRIMARY KEY (runway_id),

    CONSTRAINT uq_core_runways_source
        UNIQUE (source_runway_id),

    CONSTRAINT fk_core_runways_airport
        FOREIGN KEY (airport_id)
        REFERENCES core.airports (airport_id),

    CONSTRAINT chk_core_runways_length
        CHECK (length_ft IS NULL OR length_ft >= 0),

    CONSTRAINT chk_core_runways_width
        CHECK (width_ft IS NULL OR width_ft >= 0)
);


-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_core_regions_country_id
    ON core.regions (country_id);

CREATE INDEX idx_core_airports_region_id
    ON core.airports (region_id);

CREATE INDEX idx_core_runways_airport_id
    ON core.runways (airport_id);

COMMIT;