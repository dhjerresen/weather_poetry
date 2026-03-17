from __future__ import annotations

import sqlite3
from pathlib import Path

from config import SQL_DB_PATH


def init_db() -> sqlite3.Connection:
    """
    Initialise the SQLite database and create the weather table if needed.
    """
    db_path = Path(SQL_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            forecast_date TEXT NOT NULL,
            forecast_time TEXT NOT NULL,
            temperature_2m REAL,
            precipitation REAL,
            wind_speed_10m REAL,
            cloud_cover REAL,
            relative_humidity_2m REAL,
            UNIQUE(location_name, forecast_time)
        )
        """
    )

    conn.commit()
    return conn


def store_weather(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """
    Insert weather rows into SQLite.
    Uses INSERT OR IGNORE to avoid duplicates.
    """
    cursor = conn.cursor()
    inserted = 0

    sql = """
        INSERT OR IGNORE INTO weather_forecasts (
            location_name,
            latitude,
            longitude,
            forecast_date,
            forecast_time,
            temperature_2m,
            precipitation,
            wind_speed_10m,
            cloud_cover,
            relative_humidity_2m
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for row in rows:
        cursor.execute(
            sql,
            (
                row["location_name"],
                row["latitude"],
                row["longitude"],
                row["forecast_date"],
                row["forecast_time"],
                row["temperature_2m"],
                row["precipitation"],
                row["wind_speed_10m"],
                row["cloud_cover"],
                row["relative_humidity_2m"],
            ),
        )
        inserted += cursor.rowcount

    conn.commit()
    return inserted