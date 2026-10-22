"""Pull Garmin data for a date range into the S3 data lake (raw JSON).

Loading into Postgres is done separately by load_from_s3.py.

Usage:
  python ingestion/ingest.py --days 3
  python ingestion/ingest.py --start 2024-01-01 --end 2024-03-31
"""
import argparse
import time
from datetime import date, timedelta

from garmin_auth import get_client
from lake import get_s3, put_activities, put_json

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
    s3 = get_s3()

    fetchers = {
        "daily_summary": client.get_user_summary,
        "sleep": client.get_sleep_data,
        "heart_rate": client.get_heart_rates,
    }

    ok = failed = 0
    for d in daterange(start, end):
        day = d.isoformat()
        for name, fn in fetchers.items():
            try:
                payload = fn(day)
                if payload:
                    put_json(s3, name, day, payload)
                    ok += 1
            except Exception as e:
                failed += 1
                print(f"[WARN] {name} {day}: {type(e).__name__}: {e}")
            time.sleep(PAUSE)
        print(f"{day} done")

    try:
        acts = client.get_activities_by_date(start.isoformat(), end.isoformat())
        print(f"activities: {put_activities(s3, acts)} written")
    except Exception as e:
        failed += 1
        print(f"[WARN] activities: {type(e).__name__}: {e}")

    print(f"Finished. ok={ok} failed={failed}")


if __name__ == "__main__":
    main()
