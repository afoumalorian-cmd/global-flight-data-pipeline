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
            f"Analytics quality check failed: {check_name}. "
            f"Invalid rows: {invalid_count}"
        )


def validate_analytics_quality(connection) -> None:
    """Validate business and aggregation rules in ANALYTICS."""
    checks = (
        (
            "country_stats negative metrics",
            """
            SELECT COUNT(*)
            FROM analytics.country_stats
            WHERE region_count < 0
               OR airport_count < 0
               OR runway_count < 0
               OR lighted_runway_count < 0
               OR closed_runway_count < 0
            """,
        ),
        (
            "region_stats negative metrics",
            """
            SELECT COUNT(*)
            FROM analytics.region_stats
            WHERE airport_count < 0
               OR runway_count < 0
               OR lighted_runway_count < 0
               OR closed_runway_count < 0
            """,
        ),
        (
            "airport_stats negative metrics",
            """
            SELECT COUNT(*)
            FROM analytics.airport_stats
            WHERE runway_count < 0
               OR lighted_runway_count < 0
               OR closed_runway_count < 0
            """,
        ),
        (
            "country runway metric consistency",
            """
            SELECT COUNT(*)
            FROM analytics.country_stats
            WHERE lighted_runway_count > runway_count
               OR closed_runway_count > runway_count
            """,
        ),
        (
            "region runway metric consistency",
            """
            SELECT COUNT(*)
            FROM analytics.region_stats
            WHERE lighted_runway_count > runway_count
               OR closed_runway_count > runway_count
            """,
        ),
        (
            "airport runway metric consistency",
            """
            SELECT COUNT(*)
            FROM analytics.airport_stats
            WHERE lighted_runway_count > runway_count
               OR closed_runway_count > runway_count
            """,
        ),
        (
            "country scheduled service consistency",
            """
            SELECT COUNT(*)
            FROM analytics.country_stats
            WHERE scheduled_service_airport_count > airport_count
            """,
        ),
        (
            "region scheduled service consistency",
            """
            SELECT COUNT(*)
            FROM analytics.region_stats
            WHERE scheduled_service_airport_count > airport_count
            """,
        ),
        (
            "airport geographic consistency",
            """
            SELECT COUNT(*)
            FROM analytics.airport_stats ast
            JOIN core.airports a
                ON a.airport_id = ast.airport_id
            JOIN core.regions r
                ON r.region_id = a.region_id
            JOIN core.countries c
                ON c.country_id = r.country_id
            WHERE ast.region_id IS DISTINCT FROM r.region_id
               OR ast.region_code IS DISTINCT FROM r.code
               OR ast.region_name IS DISTINCT FROM r.name
               OR ast.country_id IS DISTINCT FROM c.country_id
               OR ast.country_code IS DISTINCT FROM c.code
               OR ast.country_name IS DISTINCT FROM c.name
            """,
        ),
        (
            "unknown airport types",
            """
            SELECT COUNT(*)
            FROM core.airports
            WHERE type NOT IN (
                'large_airport',
                'medium_airport',
                'small_airport',
                'heliport',
                'seaplane_base',
                'balloonport',
                'closed'
            )
            """,
        ),
        (
            "global airport type reconciliation",
            """
            SELECT COUNT(*)
            FROM analytics.global_summary
            WHERE total_airports <> (
                large_airport_count
                + medium_airport_count
                + small_airport_count
                + heliport_count
                + seaplane_base_count
                + balloonport_count
                + closed_airport_count
            )
            """,
        ),
        (
            "global airport aggregate consistency",
            """
            SELECT COUNT(*)
            FROM analytics.global_summary g
            WHERE g.total_airports <> (
                SELECT COALESCE(SUM(airport_count), 0)
                FROM analytics.country_stats
            )
            """,
        ),
        (
            "global runway aggregate consistency",
            """
            SELECT COUNT(*)
            FROM analytics.global_summary g
            WHERE g.total_runways <> (
                SELECT COALESCE(SUM(runway_count), 0)
                FROM analytics.country_stats
            )
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
        "All ANALYTICS Data Quality checks passed"
    )