-- ============================================================
-- Global Flight Data Pipeline
-- RAW -> STAGING transformations
--
-- Purpose:
--   Clean and standardize OurAirports raw datasets before
--   loading them into the staging layer.
--
-- Principles:
--   - RAW data is never modified.
--   - Empty strings are normalized to NULL.
--   - Codes are trimmed and normalized to uppercase.
--   - Invalid numerical values are converted to NULL.
--   - Boolean-like source values are converted to BOOLEAN.
--   - Source lineage metadata is preserved.
-- ============================================================


-- ============================================================
-- Reset staging tables
-- ============================================================

TRUNCATE TABLE
    staging.runways,
    staging.regions,
    staging.countries,
    staging.airports;


-- ============================================================
-- Airports
-- ============================================================

INSERT INTO staging.airports (
    id,
    ident,
    type,
    name,
    latitude_deg,
    longitude_deg,
    elevation_ft,
    continent,
    iso_country,
    iso_region,
    municipality,
    scheduled_service,
    gps_code,
    icao_code,
    iata_code,
    local_code,
    home_link,
    wikipedia_link,
    keywords,
    ingested_at,
    source_file
)
SELECT
    id,

    UPPER(BTRIM(ident)),

    NULLIF(BTRIM(type), ''),
    NULLIF(BTRIM(name), ''),

    CASE
        WHEN latitude_deg BETWEEN -90 AND 90
        THEN latitude_deg
        ELSE NULL
    END,

    CASE
        WHEN longitude_deg BETWEEN -180 AND 180
        THEN longitude_deg
        ELSE NULL
    END,

    elevation_ft,

    UPPER(NULLIF(BTRIM(continent), '')),
    UPPER(NULLIF(BTRIM(iso_country), '')),
    UPPER(NULLIF(BTRIM(iso_region), '')),

    NULLIF(BTRIM(municipality), ''),

    CASE
        WHEN LOWER(BTRIM(scheduled_service)) = 'yes' THEN TRUE
        WHEN LOWER(BTRIM(scheduled_service)) = 'no' THEN FALSE
        ELSE NULL
    END,

    UPPER(NULLIF(BTRIM(gps_code), '')),
    UPPER(NULLIF(BTRIM(icao_code), '')),
    UPPER(NULLIF(BTRIM(iata_code), '')),
    UPPER(NULLIF(BTRIM(local_code), '')),

    NULLIF(BTRIM(home_link), ''),
    NULLIF(BTRIM(wikipedia_link), ''),
    NULLIF(BTRIM(keywords), ''),

    ingested_at,
    source_file

FROM raw.airports;


-- ============================================================
-- Countries
-- ============================================================

INSERT INTO staging.countries (
    id,
    code,
    name,
    continent,
    wikipedia_link,
    keywords,
    ingested_at,
    source_file
)
SELECT
    id,

    UPPER(BTRIM(code)),
    NULLIF(BTRIM(name), ''),
    UPPER(NULLIF(BTRIM(continent), '')),

    NULLIF(BTRIM(wikipedia_link), ''),
    NULLIF(BTRIM(keywords), ''),

    ingested_at,
    source_file

FROM raw.countries;


-- ============================================================
-- Regions
-- ============================================================

INSERT INTO staging.regions (
    id,
    code,
    local_code,
    name,
    continent,
    iso_country,
    wikipedia_link,
    keywords,
    ingested_at,
    source_file
)
SELECT
    id,

    UPPER(BTRIM(code)),
    UPPER(NULLIF(BTRIM(local_code), '')),

    NULLIF(BTRIM(name), ''),

    UPPER(NULLIF(BTRIM(continent), '')),
    UPPER(NULLIF(BTRIM(iso_country), '')),

    NULLIF(BTRIM(wikipedia_link), ''),
    NULLIF(BTRIM(keywords), ''),

    ingested_at,
    source_file

FROM raw.regions;


-- ============================================================
-- Runways
-- ============================================================

INSERT INTO staging.runways (
    id,
    airport_ref,
    airport_ident,
    length_ft,
    width_ft,
    surface,
    lighted,
    closed,
    le_ident,
    le_latitude_deg,
    le_longitude_deg,
    le_elevation_ft,
    le_heading_degt,
    le_displaced_threshold_ft,
    he_ident,
    he_latitude_deg,
    he_longitude_deg,
    he_elevation_ft,
    he_heading_degt,
    he_displaced_threshold_ft,
    ingested_at,
    source_file
)
SELECT
    id,
    airport_ref,

    UPPER(NULLIF(BTRIM(airport_ident), '')),

    CASE
        WHEN length_ft >= 0 THEN length_ft
        ELSE NULL
    END,

    CASE
        WHEN width_ft >= 0 THEN width_ft
        ELSE NULL
    END,

    NULLIF(BTRIM(surface), ''),

    CASE
        WHEN lighted = 1 THEN TRUE
        WHEN lighted = 0 THEN FALSE
        ELSE NULL
    END,

    CASE
        WHEN closed = 1 THEN TRUE
        WHEN closed = 0 THEN FALSE
        ELSE NULL
    END,

    UPPER(NULLIF(BTRIM(le_ident), '')),

    CASE
        WHEN le_latitude_deg BETWEEN -90 AND 90
        THEN le_latitude_deg
        ELSE NULL
    END,

    CASE
        WHEN le_longitude_deg BETWEEN -180 AND 180
        THEN le_longitude_deg
        ELSE NULL
    END,

    le_elevation_ft,
    le_heading_degt,

    CASE
        WHEN le_displaced_threshold_ft >= 0
        THEN le_displaced_threshold_ft
        ELSE NULL
    END,

    UPPER(NULLIF(BTRIM(he_ident), '')),

    CASE
        WHEN he_latitude_deg BETWEEN -90 AND 90
        THEN he_latitude_deg
        ELSE NULL
    END,

    CASE
        WHEN he_longitude_deg BETWEEN -180 AND 180
        THEN he_longitude_deg
        ELSE NULL
    END,

    he_elevation_ft,
    he_heading_degt,

    CASE
        WHEN he_displaced_threshold_ft >= 0
        THEN he_displaced_threshold_ft
        ELSE NULL
    END,

    ingested_at,
    source_file

FROM raw.runways;
