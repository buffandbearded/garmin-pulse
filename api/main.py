"""Read-only REST API over the dbt marts layer."""
import os
from datetime import date

import psycopg2
from fastapi import Depends, FastAPI, Query
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Garmin Pulse API",
    version="1.0.0",
    description="Read-only access to the dbt marts built from my Garmin Connect data.",
)


def get_cursor():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=5432,
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
    finally:
        conn.close()


@app.get("/health")
def health(cur=Depends(get_cursor)):
    cur.execute("select max(calendar_date) as latest_day from marts.fct_daily_health")
    return {"status": "ok", **cur.fetchone()}


@app.get("/daily")
def daily(
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(90, ge=1, le=1000),
    cur=Depends(get_cursor),
):
    cur.execute(
        """
        select * from marts.fct_daily_health
        where (%(start)s::date is null or calendar_date >= %(start)s)
          and (%(end)s::date is null or calendar_date <= %(end)s)
        order by calendar_date desc
        limit %(limit)s
        """,
        {"start": start, "end": end, "limit": limit},
    )
    return cur.fetchall()


@app.get("/weekly")
def weekly(limit: int = Query(52, ge=1, le=520), cur=Depends(get_cursor)):
    cur.execute(
        "select * from marts.fct_weekly_summary order by week_start desc limit %s",
        (limit,),
    )
    return cur.fetchall()


@app.get("/workouts")
def workouts(
    activity_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    cur=Depends(get_cursor),
):
    cur.execute(
        """
        select * from marts.fct_workouts
        where (%(t)s::text is null or activity_type = %(t)s)
        order by start_time_local desc
        limit %(limit)s
        """,
        {"t": activity_type, "limit": limit},
    )
    return cur.fetchall()
