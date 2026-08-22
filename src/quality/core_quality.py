import logging


logger = logging.getLogger(__name__)


def run_zero_count_check(
    cursor,
    check_name: str,
    query: str,
) -> None:
    """Run a quality check that must return zero invalid rows."""
    cursor.execute(query)

    invalid_count = cursor.fetchone()[0]

    logger.info(
        "%s: invalid_rows=%s",
        check_name,
        invalid_count,
    )

    if invalid_count != 0:
        raise RuntimeError(
            f"Core quality check failed: {check_name}. "
            f"Invalid rows: {invalid_count}"
        )


def validate_core_quality(connection) -> None:
    """Validate relational and business rules in CORE."""
    checks = (
        (
            "regions without country",
            """
            SELECT COUNT(*)
            FROM core.regions r
            LEFT JOIN core.countries c
                ON c.country_id = r.country_id
            WHERE c.country_id IS NULL
            """,
        ),
        (
            "airports without region",
            """
            SELECT COUNT(*)
            FROM core.airports a
            LEFT JOIN core.regions r
                ON r.region_id = a.region_id
            WHERE r.region_id IS NULL
            """,
        ),
        (
            "runways without airport",
            """
            SELECT COUNT(*)
            FROM core.runways rw
            LEFT JOIN core.airports a
                ON a.airport_id = rw.airport_id
            WHERE a.airport_id IS NULL
            """,
        ),
        (
            "invalid airport latitude",
            """
            SELECT COUNT(*)
            FROM core.airports
            WHERE latitude_deg NOT BETWEEN -90 AND 90
            """,
        ),
        (
            "invalid airport longitude",
            """
            SELECT COUNT(*)
            FROM core.airports
            WHERE longitude_deg NOT BETWEEN -180 AND 180
            """,
        ),
        (
            "negative runway length",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE length_ft < 0
            """,
        ),
        (
            "negative runway width",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE width_ft < 0
            """,
        ),
        (
            "invalid runway low-end latitude",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE le_latitude_deg IS NOT NULL
              AND le_latitude_deg NOT BETWEEN -90 AND 90
            """,
        ),
        (
            "invalid runway low-end longitude",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE le_longitude_deg IS NOT NULL
              AND le_longitude_deg NOT BETWEEN -180 AND 180
            """,
        ),
        (
            "invalid runway high-end latitude",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE he_latitude_deg IS NOT NULL
              AND he_latitude_deg NOT BETWEEN -90 AND 90
            """,
        ),
        (
            "invalid runway high-end longitude",
            """
            SELECT COUNT(*)
            FROM core.runways
            WHERE he_longitude_deg IS NOT NULL
              AND he_longitude_deg NOT BETWEEN -180 AND 180
            """,
        ),
        (
            "region country mapping consistency",
            """
            SELECT COUNT(*)
            FROM core.regions r
            JOIN core.countries c
                ON c.country_id = r.country_id
            JOIN staging.regions sr
                ON sr.id = r.source_region_id
            WHERE sr.iso_country IS DISTINCT FROM c.code
            """,
        ),
        (
            "airport region mapping consistency",
            """
            SELECT COUNT(*)
            FROM core.airports a
            JOIN core.regions r
                ON r.region_id = a.region_id
            JOIN staging.airports sa
                ON sa.id = a.source_airport_id
            WHERE sa.iso_region IS DISTINCT FROM r.code
            """,
        ),
        (
            "runway airport mapping consistency",
            """
            SELECT COUNT(*)
            FROM core.runways rw
            JOIN core.airports a
                ON a.airport_id = rw.airport_id
            JOIN staging.runways sr
                ON sr.id = rw.source_runway_id
            WHERE sr.airport_ref IS DISTINCT FROM a.source_airport_id
            """,
        ),
    )

    with connection.cursor() as cursor:
        for check_name, query in checks:
            run_zero_count_check(
                cursor,
                check_name,
                query,
            )

    logger.info(
        "All CORE Data Quality checks passed"
    )