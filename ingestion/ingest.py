"""Pull Garmin data for a date range into raw.* tables (idempotent).

Usage:
  python ingestion/ingest.py --days 3
  python ingestion/ingest.py --start 2024-01-01 --end 2024-03-31
"""
import argparse
import time
from datetime import date, timedelta

from db import get_conn, init_schema, upsert_activities, upsert_daily
from garmin_auth import get_client

PAUSE = 0.7  # seconds between API calls, to stay under rate limits


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=date.fromisoformat)
    p.add_argument("--end", type=date.fromisoformat, default=date.today())
    p.add_argument("--days", type=int, help="last N days (overrides --start)")
    args = p.parse_args()

    end = args.end
    start = end - timedelta(days=args.days - 1) if args.days else args.start
    if start is None:
        p.error("give --days N or --start YYYY-MM-DD")

    client = get_client()
    conn = get_conn()
    init_schema(conn)

    fetchers = {
        "daily_summary": client.get_user_summary,
        "sleep": client.get_sleep_data,
        "heart_rate": client.get_heart_rates,
    }

    ok = failed = 0
    for d in daterange(start, end):
        day = d.isoformat()
        for table, fn in fetchers.items():
            try:
                payload = fn(day)
                if payload:
                    upsert_daily(conn, table, day, payload)
                    ok += 1
            except Exception as e:
                failed += 1
                conn.rollback()
                print(f"[WARN] {table} {day}: {type(e).__name__}: {e}")
            time.sleep(PAUSE)
        print(f"{day} done")

    try:
        acts = client.get_activities_by_date(start.isoformat(), end.isoformat())
        n = upsert_activities(conn, acts)
        print(f"activities: {n} upserted")
    except Exception as e:
        failed += 1
        conn.rollback()
        print(f"[WARN] activities: {type(e).__name__}: {e}")

    conn.close()
    print(f"Finished. ok={ok} failed={failed}")


if __name__ == "__main__":
    main()
