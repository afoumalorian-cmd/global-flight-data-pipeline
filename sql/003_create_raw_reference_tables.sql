CREATE TABLE IF NOT EXISTS raw.countries (
    id BIGINT,
    code TEXT,
    name TEXT,
    continent TEXT,
    wikipedia_link TEXT,
    keywords TEXT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);


CREATE TABLE IF NOT EXISTS raw.regions (
    id BIGINT,
    code TEXT,
    local_code TEXT,
    name TEXT,
    continent TEXT,
    iso_country TEXT,
    wikipedia_link TEXT,
    keywords TEXT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT
);