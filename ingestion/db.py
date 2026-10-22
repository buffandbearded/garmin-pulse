"""Postgres helpers: connection, raw table DDL, idempotent upserts."""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DAILY_TABLES = ["daily_summary", "sleep", "heart_rate"]

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;
""" + "".join(
    f"""
CREATE TABLE IF NOT EXISTS raw.garmin_{t} (
    calendar_date date PRIMARY KEY,
    payload       jsonb NOT NULL,
    ingested_at   timestamptz NOT NULL DEFAULT now()
);
"""
    for t in DAILY_TABLES
) + """
CREATE TABLE IF NOT EXISTS raw.garmin_activities (
    activity_id      bigint PRIMARY KEY,
    start_time_local timestamp,
    payload          jsonb NOT NULL,
    ingested_at      timestamptz NOT NULL DEFAULT now()
);
"""


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def init_schema(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()


def upsert_daily(conn, table: str, day: str, payload) -> None:
    assert table in DAILY_TABLES
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO raw.garmin_{table} (calendar_date, payload)
            VALUES (%s, %s)
            ON CONFLICT (calendar_date)
            DO UPDATE SET payload = EXCLUDED.payload, ingested_at = now()
            """,
            (day, Json(payload)),
        )
    conn.commit()


def upsert_activities(conn, activities: list) -> int:
    with conn.cursor() as cur:
        for a in activities:
            cur.execute(
                """
                INSERT INTO raw.garmin_activities (activity_id, start_time_local, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (activity_id)
                DO UPDATE SET payload = EXCLUDED.payload, ingested_at = now()
                """,
                (a["activityId"], a.get("startTimeLocal"), Json(a)),
            )
    conn.commit()
    return len(activities)
