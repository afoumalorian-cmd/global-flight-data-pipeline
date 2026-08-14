CREATE TABLE IF NOT EXISTS raw.runways (
    id BIGINT,
    airport_ref BIGINT,
    airport_ident TEXT,
    length_ft DOUBLE PRECISION,
    width_ft DOUBLE PRECISION,
    surface TEXT,
    lighted INTEGER,
    closed INTEGER,

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

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);