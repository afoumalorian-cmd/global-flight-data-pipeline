-- ============================================================
-- Global Flight Data Pipeline
-- Analytics Layer - Table Creation
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.global_summary (
    summary_id SMALLINT NOT NULL DEFAULT 1,

    -- Global entity counts
    total_countries BIGINT NOT NULL,
    total_regions BIGINT NOT NULL,
    total_airports BIGINT NOT NULL,
    total_runways BIGINT NOT NULL,

    -- Airport counts by type
    large_airport_count BIGINT NOT NULL,
    medium_airport_count BIGINT NOT NULL,
    small_airport_count BIGINT NOT NULL,
    heliport_count BIGINT NOT NULL,
    seaplane_base_count BIGINT NOT NULL,
    balloonport_count BIGINT NOT NULL,
    closed_airport_count BIGINT NOT NULL,

    -- Airport operational metrics
    scheduled_service_airport_count BIGINT NOT NULL,

    -- Runway metrics
    lighted_runway_count BIGINT NOT NULL,
    closed_runway_count BIGINT NOT NULL,
    avg_runway_length_ft NUMERIC(12, 2),
    max_runway_length_ft INTEGER,

    -- Metadata
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_analytics_global_summary
        PRIMARY KEY (summary_id),

    CONSTRAINT chk_analytics_global_summary_single_row
        CHECK (summary_id = 1)
);

-- ============================================================
-- Country-level analytics
-- Grain: one row per country
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.country_stats (
    country_id BIGINT NOT NULL,
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,
    continent_code TEXT,

    -- Geographic metrics
    region_count BIGINT NOT NULL,

    -- Airport metrics
    airport_count BIGINT NOT NULL,
    large_airport_count BIGINT NOT NULL,
    medium_airport_count BIGINT NOT NULL,
    small_airport_count BIGINT NOT NULL,
    heliport_count BIGINT NOT NULL,
    seaplane_base_count BIGINT NOT NULL,
    balloonport_count BIGINT NOT NULL,
    closed_airport_count BIGINT NOT NULL,
    scheduled_service_airport_count BIGINT NOT NULL,

    -- Runway metrics
    runway_count BIGINT NOT NULL,
    lighted_runway_count BIGINT NOT NULL,
    closed_runway_count BIGINT NOT NULL,
    avg_runway_length_ft NUMERIC(12, 2),
    max_runway_length_ft INTEGER,

    -- Metadata
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_analytics_country_stats
        PRIMARY KEY (country_id),

    CONSTRAINT uq_analytics_country_stats_code
        UNIQUE (country_code)
);

-- ============================================================
-- Region-level analytics
-- Grain: one row per region
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.region_stats (
    region_id BIGINT NOT NULL,
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL,

    -- Country information
    country_id BIGINT NOT NULL,
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,

    -- Airport metrics
    airport_count BIGINT NOT NULL,
    large_airport_count BIGINT NOT NULL,
    medium_airport_count BIGINT NOT NULL,
    small_airport_count BIGINT NOT NULL,
    heliport_count BIGINT NOT NULL,
    seaplane_base_count BIGINT NOT NULL,
    balloonport_count BIGINT NOT NULL,
    closed_airport_count BIGINT NOT NULL,
    scheduled_service_airport_count BIGINT NOT NULL,

    -- Runway metrics
    runway_count BIGINT NOT NULL,
    lighted_runway_count BIGINT NOT NULL,
    closed_runway_count BIGINT NOT NULL,
    avg_runway_length_ft NUMERIC(12, 2),
    max_runway_length_ft INTEGER,

    -- Metadata
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_analytics_region_stats
        PRIMARY KEY (region_id),

    CONSTRAINT uq_analytics_region_stats_code
        UNIQUE (region_code)
);

-- ============================================================
-- Airport-level analytics
-- Grain: one row per airport
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.airport_stats (
    airport_id BIGINT NOT NULL,
    airport_ident TEXT NOT NULL,
    airport_name TEXT NOT NULL,
    airport_type TEXT NOT NULL,

    -- Geographic information
    country_id BIGINT NOT NULL,
    country_code TEXT NOT NULL,
    country_name TEXT NOT NULL,

    region_id BIGINT NOT NULL,
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL,

    municipality TEXT,

    latitude_deg DOUBLE PRECISION NOT NULL,
    longitude_deg DOUBLE PRECISION NOT NULL,
    elevation_ft INTEGER,

    -- Airport operational information
    scheduled_service BOOLEAN NOT NULL,

    -- Runway metrics
    runway_count BIGINT NOT NULL,
    lighted_runway_count BIGINT NOT NULL,
    closed_runway_count BIGINT NOT NULL,

    avg_runway_length_ft NUMERIC(12, 2),
    max_runway_length_ft INTEGER,

    avg_runway_width_ft NUMERIC(12, 2),
    max_runway_width_ft INTEGER,

    -- Metadata
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_analytics_airport_stats
        PRIMARY KEY (airport_id),

    CONSTRAINT uq_analytics_airport_stats_ident
        UNIQUE (airport_ident)
);