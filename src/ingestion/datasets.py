from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OURAIRPORTS_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ourairports"


DATASETS = {
    "airports": {
        "table": "airports",
        "file_path": OURAIRPORTS_RAW_DIR / "airports.csv",
        "columns": [
            "id",
            "ident",
            "type",
            "name",
            "latitude_deg",
            "longitude_deg",
            "elevation_ft",
            "continent",
            "iso_country",
            "iso_region",
            "municipality",
            "scheduled_service",
            "icao_code",
            "iata_code",
            "gps_code",
            "local_code",
            "home_link",
            "wikipedia_link",
            "keywords",
        ],
    },
    "countries": {
        "table": "countries",
        "file_path": OURAIRPORTS_RAW_DIR / "countries.csv",
        "columns": [
            "id",
            "code",
            "name",
            "continent",
            "wikipedia_link",
            "keywords",
        ],
    },
    "regions": {
        "table": "regions",
        "file_path": OURAIRPORTS_RAW_DIR / "regions.csv",
        "columns": [
            "id",
            "code",
            "local_code",
            "name",
            "continent",
            "iso_country",
            "wikipedia_link",
            "keywords",
        ],
    },
}