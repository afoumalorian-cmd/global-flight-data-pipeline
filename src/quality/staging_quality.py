import logging


logger = logging.getLogger(__name__)


FAILURE_CHECKS = {
    "airports_invalid_latitude": """
        SELECT COUNT(*)
        FROM staging.airports
        WHERE latitude_deg IS NOT NULL
          AND latitude_deg NOT BETWEEN -90 AND 90
    """,
    "airports_invalid_longitude": """
        SELECT COUNT(*)
        FROM staging.airports
        WHERE longitude_deg IS NOT NULL
         AND longitude_deg NOT BETWEEN -180 AND 180
    """,
    "runways_negative_length": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE length_ft < 0
    """,
    "runways_negative_width": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE width_ft < 0
    """,
    "runways_invalid_le_latitude": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE le_latitude_deg IS NOT NULL
          AND le_latitude_deg NOT BETWEEN -90 AND 90
    """,
    "runways_invalid_le_longitude": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE le_longitude_deg IS NOT NULL
          AND le_longitude_deg NOT BETWEEN -180 AND 180
    """,
    "runways_invalid_he_latitude": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE he_latitude_deg IS NOT NULL
          AND he_latitude_deg NOT BETWEEN -90 AND 90
    """,
    "runways_invalid_he_longitude": """
        SELECT COUNT(*)
        FROM staging.runways
        WHERE he_longitude_deg IS NOT NULL
          AND he_longitude_deg NOT BETWEEN -180 AND 180
    """,
    "airports_without_region": """
        SELECT COUNT(*)
        FROM staging.airports a
        LEFT JOIN staging.regions r
            ON a.iso_region = r.code
        WHERE a.iso_region IS NOT NULL
          AND r.code IS NULL
    """,
    "inconsistent_runway_airport_references": """
        SELECT COUNT(*)
        FROM staging.runways r
        JOIN staging.airports a
            ON r.airport_ref = a.id
        WHERE r.airport_ident IS NOT NULL
          AND r.airport_ident <> a.ident
    """,
}


WARNING_CHECKS = {
    "runways_without_airport": """
        SELECT COUNT(*)
        FROM staging.runways r
        LEFT JOIN staging.airports a
            ON r.airport_ident = a.ident
        WHERE r.airport_ident IS NOT NULL
          AND a.ident IS NULL
    """,
    "regions_without_country": """
        SELECT COUNT(*)
        FROM staging.regions r
        LEFT JOIN staging.countries c
            ON r.iso_country = c.code
        WHERE r.iso_country IS NOT NULL
          AND c.code IS NULL
    """,
    "airports_without_country": """
        SELECT COUNT(*)
        FROM staging.airports a
        LEFT JOIN staging.countries c
            ON a.iso_country = c.code
        WHERE a.iso_country IS NOT NULL
          AND c.code IS NULL
    """,
    "runways_without_airport_ref": """
        SELECT COUNT(*)
        FROM staging.runways r
        LEFT JOIN staging.airports a
            ON r.airport_ref = a.id
        WHERE r.airport_ref IS NOT NULL
          AND a.id IS NULL
    """,
}


def _execute_count_check(cursor, query: str) -> int:
    """Execute a quality check query and return its violation count."""
    cursor.execute(query)
    return cursor.fetchone()[0]


def validate_staging_quality(connection) -> None:
    """Run blocking and non-blocking Data Quality checks on STAGING."""
    with connection.cursor() as cursor:
        for check_name, query in FAILURE_CHECKS.items():
            violation_count = _execute_count_check(
                cursor,
                query,
            )

            if violation_count > 0:
                raise RuntimeError(
                    f"Data Quality check failed: "
                    f"{check_name}={violation_count}"
                )

            logger.info(
                "Data Quality check passed: %s",
                check_name,
            )

        for check_name, query in WARNING_CHECKS.items():
            violation_count = _execute_count_check(
                cursor,
                query,
            )

            if violation_count > 0:
                logger.warning(
                    "Data Quality warning: %s=%s",
                    check_name,
                    violation_count,
                )
            else:
                logger.info(
                    "Data Quality check passed: %s",
                    check_name,
                )