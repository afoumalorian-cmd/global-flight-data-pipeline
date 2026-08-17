-- =============================================================================
-- Migration: 008_transform_staging_to_core.sql
-- Purpose: Transform and load trusted STAGING data into CORE
-- =============================================================================

BEGIN;

-- =============================================================================
-- Reset CORE tables
-- =============================================================================

TRUNCATE TABLE
    core.runways,
    core.airports,
    core.regions,
    core.countries
RESTART IDENTITY CASCADE;


-- =============================================================================
-- COUNTRIES
-- =============================================================================

INSERT INTO core.countries (
    source_country_id,
    code,
    name,
    continent_code,
    wikipedia_link,
    keywords
)
SELECT
    id,
    code,
    name,
    continent,
    wikipedia_link,
    keywords
FROM staging.countries;


-- =============================================================================
-- REGIONS
-- =============================================================================

INSERT INTO core.regions (
    source_region_id,
    country_id,
    code,
    local_code,
    name,
    wikipedia_link,
    keywords
)
SELECT
    sr.id,
    cc.country_id,
    sr.code,
    sr.local_code,
    sr.name,
    sr.wikipedia_link,
    sr.keywords
FROM staging.regions sr
JOIN core.countries cc
    ON cc.code = sr.iso_country;


-- =============================================================================
-- AIRPORTS
-- =============================================================================

INSERT INTO core.airports (
    source_airport_id,
    region_id,
    ident,
    type,
    name,
    latitude_deg,
    longitude_deg,
    elevation_ft,
    municipality,
    scheduled_service,
    gps_code,
    icao_code,
    iata_code,
    local_code,
    home_link,
    wikipedia_link,
    keywords
)
SELECT
    sa.id,
    cr.region_id,
    sa.ident,
    sa.type,
    sa.name,
    sa.latitude_deg,
    sa.longitude_deg,
    sa.elevation_ft,
    sa.municipality,
    sa.scheduled_service,
    sa.gps_code,
    sa.icao_code,
    sa.iata_code,
    sa.local_code,
    sa.home_link,
    sa.wikipedia_link,
    sa.keywords
FROM staging.airports sa
JOIN core.regions cr
    ON cr.code = sa.iso_region;


-- =============================================================================
-- RUNWAYS
-- =============================================================================

INSERT INTO core.runways (
    source_runway_id,
    airport_id,
    length_ft,
    width_ft,
    surface,
    lighted,
    closed,
    le_ident,
    le_latitude_deg,
    le_longitude_deg,
    he_ident,
    he_latitude_deg,
    he_longitude_deg
)
SELECT
    sr.id,
    ca.airport_id,
    sr.length_ft,
    sr.width_ft,
    sr.surface,
    sr.lighted,
    sr.closed,
    sr.le_ident,
    sr.le_latitude_deg,
    sr.le_longitude_deg,
    sr.he_ident,
    sr.he_latitude_deg,
    sr.he_longitude_deg
FROM staging.runways sr
JOIN core.airports ca
    ON ca.source_airport_id = sr.airport_ref;


COMMIT;