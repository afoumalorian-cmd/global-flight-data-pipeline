-- ============================================================
-- Global Flight Data Pipeline
-- CORE -> ANALYTICS Transformation
-- ============================================================

-- ============================================================
-- Refresh analytics tables
-- ============================================================

TRUNCATE TABLE
    analytics.global_summary,
    analytics.country_stats,
    analytics.region_stats,
    analytics.airport_stats;


-- ============================================================
-- 1. GLOBAL SUMMARY
-- Grain: one row for the entire dataset
-- ============================================================

WITH airport_metrics AS (
    SELECT
        COUNT(*) AS total_airports,

        COUNT(*) FILTER (
            WHERE type = 'large_airport'
        ) AS large_airport_count,

        COUNT(*) FILTER (
            WHERE type = 'medium_airport'
        ) AS medium_airport_count,

        COUNT(*) FILTER (
            WHERE type = 'small_airport'
        ) AS small_airport_count,

        COUNT(*) FILTER (
            WHERE type = 'heliport'
        ) AS heliport_count,

        COUNT(*) FILTER (
            WHERE type = 'seaplane_base'
        ) AS seaplane_base_count,

        COUNT(*) FILTER (
            WHERE type = 'balloonport'
        ) AS balloonport_count,

        COUNT(*) FILTER (
            WHERE type = 'closed'
        ) AS closed_airport_count,

        COUNT(*) FILTER (
            WHERE scheduled_service = TRUE
        ) AS scheduled_service_airport_count

    FROM core.airports
),

runway_metrics AS (
    SELECT
        COUNT(*) AS total_runways,

        COUNT(*) FILTER (
            WHERE lighted = TRUE
        ) AS lighted_runway_count,

        COUNT(*) FILTER (
            WHERE closed = TRUE
        ) AS closed_runway_count,

        ROUND(AVG(length_ft), 2) AS avg_runway_length_ft,

        MAX(length_ft) AS max_runway_length_ft

    FROM core.runways
)

INSERT INTO analytics.global_summary (
    summary_id,
    total_countries,
    total_regions,
    total_airports,
    total_runways,
    large_airport_count,
    medium_airport_count,
    small_airport_count,
    heliport_count,
    seaplane_base_count,
    balloonport_count,
    closed_airport_count,
    scheduled_service_airport_count,
    lighted_runway_count,
    closed_runway_count,
    avg_runway_length_ft,
    max_runway_length_ft
)

SELECT
    1,
    (SELECT COUNT(*) FROM core.countries),
    (SELECT COUNT(*) FROM core.regions),
    a.total_airports,
    r.total_runways,
    a.large_airport_count,
    a.medium_airport_count,
    a.small_airport_count,
    a.heliport_count,
    a.seaplane_base_count,
    a.balloonport_count,
    a.closed_airport_count,
    a.scheduled_service_airport_count,
    r.lighted_runway_count,
    r.closed_runway_count,
    r.avg_runway_length_ft,
    r.max_runway_length_ft
FROM airport_metrics a
CROSS JOIN runway_metrics r;


-- ============================================================
-- 2. COUNTRY STATS
-- Grain: one row per country
-- ============================================================

WITH region_metrics AS (
    SELECT
        country_id,
        COUNT(*) AS region_count
    FROM core.regions
    GROUP BY country_id
),

airport_metrics AS (
    SELECT
        r.country_id,

        COUNT(a.airport_id) AS airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'large_airport'
        ) AS large_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'medium_airport'
        ) AS medium_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'small_airport'
        ) AS small_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'heliport'
        ) AS heliport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'seaplane_base'
        ) AS seaplane_base_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'balloonport'
        ) AS balloonport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'closed'
        ) AS closed_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.scheduled_service = TRUE
        ) AS scheduled_service_airport_count

    FROM core.regions r
    LEFT JOIN core.airports a
        ON a.region_id = r.region_id

    GROUP BY r.country_id
),

runway_metrics AS (
    SELECT
        r.country_id,

        COUNT(rw.runway_id) AS runway_count,

        COUNT(rw.runway_id) FILTER (
            WHERE rw.lighted = TRUE
        ) AS lighted_runway_count,

        COUNT(rw.runway_id) FILTER (
            WHERE rw.closed = TRUE
        ) AS closed_runway_count,

        ROUND(AVG(rw.length_ft), 2) AS avg_runway_length_ft,

        MAX(rw.length_ft) AS max_runway_length_ft

    FROM core.regions r

    JOIN core.airports a
        ON a.region_id = r.region_id

    JOIN core.runways rw
        ON rw.airport_id = a.airport_id

    GROUP BY r.country_id
)

INSERT INTO analytics.country_stats (
    country_id,
    country_code,
    country_name,
    continent_code,
    region_count,
    airport_count,
    large_airport_count,
    medium_airport_count,
    small_airport_count,
    heliport_count,
    seaplane_base_count,
    balloonport_count,
    closed_airport_count,
    scheduled_service_airport_count,
    runway_count,
    lighted_runway_count,
    closed_runway_count,
    avg_runway_length_ft,
    max_runway_length_ft
)

SELECT
    c.country_id,
    c.code,
    c.name,
    c.continent_code,

    COALESCE(rm.region_count, 0),

    COALESCE(am.airport_count, 0),
    COALESCE(am.large_airport_count, 0),
    COALESCE(am.medium_airport_count, 0),
    COALESCE(am.small_airport_count, 0),
    COALESCE(am.heliport_count, 0),
    COALESCE(am.seaplane_base_count, 0),
    COALESCE(am.balloonport_count, 0),
    COALESCE(am.closed_airport_count, 0),
    COALESCE(am.scheduled_service_airport_count, 0),

    COALESCE(rwm.runway_count, 0),
    COALESCE(rwm.lighted_runway_count, 0),
    COALESCE(rwm.closed_runway_count, 0),

    rwm.avg_runway_length_ft,
    rwm.max_runway_length_ft

FROM core.countries c

LEFT JOIN region_metrics rm
    ON rm.country_id = c.country_id

LEFT JOIN airport_metrics am
    ON am.country_id = c.country_id

LEFT JOIN runway_metrics rwm
    ON rwm.country_id = c.country_id;


-- ============================================================
-- 3. REGION STATS
-- Grain: one row per region
-- ============================================================

WITH airport_metrics AS (
    SELECT
        r.region_id,

        COUNT(a.airport_id) AS airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'large_airport'
        ) AS large_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'medium_airport'
        ) AS medium_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'small_airport'
        ) AS small_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'heliport'
        ) AS heliport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'seaplane_base'
        ) AS seaplane_base_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'balloonport'
        ) AS balloonport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.type = 'closed'
        ) AS closed_airport_count,

        COUNT(a.airport_id) FILTER (
            WHERE a.scheduled_service = TRUE
        ) AS scheduled_service_airport_count

    FROM core.regions r

    LEFT JOIN core.airports a
        ON a.region_id = r.region_id

    GROUP BY r.region_id
),

runway_metrics AS (
    SELECT
        a.region_id,

        COUNT(rw.runway_id) AS runway_count,

        COUNT(rw.runway_id) FILTER (
            WHERE rw.lighted = TRUE
        ) AS lighted_runway_count,

        COUNT(rw.runway_id) FILTER (
            WHERE rw.closed = TRUE
        ) AS closed_runway_count,

        ROUND(AVG(rw.length_ft), 2) AS avg_runway_length_ft,

        MAX(rw.length_ft) AS max_runway_length_ft

    FROM core.airports a

    JOIN core.runways rw
        ON rw.airport_id = a.airport_id

    GROUP BY a.region_id
)

INSERT INTO analytics.region_stats (
    region_id,
    region_code,
    region_name,
    country_id,
    country_code,
    country_name,
    airport_count,
    large_airport_count,
    medium_airport_count,
    small_airport_count,
    heliport_count,
    seaplane_base_count,
    balloonport_count,
    closed_airport_count,
    scheduled_service_airport_count,
    runway_count,
    lighted_runway_count,
    closed_runway_count,
    avg_runway_length_ft,
    max_runway_length_ft
)

SELECT
    r.region_id,
    r.code,
    r.name,

    c.country_id,
    c.code,
    c.name,

    COALESCE(am.airport_count, 0),
    COALESCE(am.large_airport_count, 0),
    COALESCE(am.medium_airport_count, 0),
    COALESCE(am.small_airport_count, 0),
    COALESCE(am.heliport_count, 0),
    COALESCE(am.seaplane_base_count, 0),
    COALESCE(am.balloonport_count, 0),
    COALESCE(am.closed_airport_count, 0),
    COALESCE(am.scheduled_service_airport_count, 0),

    COALESCE(rwm.runway_count, 0),
    COALESCE(rwm.lighted_runway_count, 0),
    COALESCE(rwm.closed_runway_count, 0),

    rwm.avg_runway_length_ft,
    rwm.max_runway_length_ft

FROM core.regions r

JOIN core.countries c
    ON c.country_id = r.country_id

LEFT JOIN airport_metrics am
    ON am.region_id = r.region_id

LEFT JOIN runway_metrics rwm
    ON rwm.region_id = r.region_id;


-- ============================================================
-- 4. AIRPORT STATS
-- Grain: one row per airport
-- ============================================================

WITH runway_metrics AS (
    SELECT
        airport_id,

        COUNT(runway_id) AS runway_count,

        COUNT(runway_id) FILTER (
            WHERE lighted = TRUE
        ) AS lighted_runway_count,

        COUNT(runway_id) FILTER (
            WHERE closed = TRUE
        ) AS closed_runway_count,

        ROUND(AVG(length_ft), 2) AS avg_runway_length_ft,

        MAX(length_ft) AS max_runway_length_ft,

        ROUND(AVG(width_ft), 2) AS avg_runway_width_ft,

        MAX(width_ft) AS max_runway_width_ft

    FROM core.runways

    GROUP BY airport_id
)

INSERT INTO analytics.airport_stats (
    airport_id,
    airport_ident,
    airport_name,
    airport_type,
    country_id,
    country_code,
    country_name,
    region_id,
    region_code,
    region_name,
    municipality,
    latitude_deg,
    longitude_deg,
    elevation_ft,
    scheduled_service,
    runway_count,
    lighted_runway_count,
    closed_runway_count,
    avg_runway_length_ft,
    max_runway_length_ft,
    avg_runway_width_ft,
    max_runway_width_ft
)

SELECT
    a.airport_id,
    a.ident,
    a.name,
    a.type,

    c.country_id,
    c.code,
    c.name,

    r.region_id,
    r.code,
    r.name,

    a.municipality,
    a.latitude_deg,
    a.longitude_deg,
    a.elevation_ft,
    a.scheduled_service,

    COALESCE(rwm.runway_count, 0),
    COALESCE(rwm.lighted_runway_count, 0),
    COALESCE(rwm.closed_runway_count, 0),

    rwm.avg_runway_length_ft,
    rwm.max_runway_length_ft,
    rwm.avg_runway_width_ft,
    rwm.max_runway_width_ft

FROM core.airports a

JOIN core.regions r
    ON r.region_id = a.region_id

JOIN core.countries c
    ON c.country_id = r.country_id

LEFT JOIN runway_metrics rwm
    ON rwm.airport_id = a.airport_id;