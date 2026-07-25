

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = "climate_risk.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                lat REAL,
                lon REAL,
                temperature REAL,
                humidity REAL,
                wind_speed REAL,
                precipitation REAL,
                risk_level TEXT,
                fetched_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_city_time ON readings (city, fetched_at)"
        )
        conn.commit()


def insert_reading(city, country, lat, lon, temperature, humidity, wind_speed, precipitation, risk_level):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO readings
                (city, country, lat, lon, temperature, humidity, wind_speed, precipitation, risk_level, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                city,
                country,
                lat,
                lon,
                temperature,
                humidity,
                wind_speed,
                precipitation,
                risk_level,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def get_latest_reading(city):
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT city, country, lat, lon, temperature, humidity, wind_speed,
                   precipitation, risk_level, fetched_at
            FROM readings
            WHERE city = ?
            ORDER BY fetched_at DESC
            LIMIT 1
            """,
            (city,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        keys = [
            "city", "country", "lat", "lon", "temperature", "humidity",
            "wind_speed", "precipitation", "risk_level", "fetched_at",
        ]
        return dict(zip(keys, row))


def is_stale(fetched_at_iso: str, max_age_hours: float) -> bool:
    fetched_at = datetime.fromisoformat(fetched_at_iso)
    return datetime.utcnow() - fetched_at > timedelta(hours=max_age_hours)


def get_history(city, limit=50):
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT temperature, humidity, wind_speed, precipitation, risk_level, fetched_at
            FROM readings
            WHERE city = ?
            ORDER BY fetched_at DESC
            LIMIT ?
            """,
            (city, limit),
        )
        rows = cur.fetchall()
        keys = ["temperature", "humidity", "wind_speed", "precipitation", "risk_level", "fetched_at"]
        return [dict(zip(keys, r)) for r in reversed(rows)]
