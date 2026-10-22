"""Load raw JSON from the S3 data lake into the raw.* Postgres tables (idempotent).

Usage:
  python ingestion/load_from_s3.py            # everything in the lake
  python ingestion/load_from_s3.py --days 3   # only the last 3 days
"""
import argparse
import json
from datetime import date, datetime, timedelta, timezone

from db import DAILY_TABLES, get_conn, init_schema, upsert_activities, upsert_daily
from lake import BUCKET, get_s3


def list_objects(s3, prefix):
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=prefix):
        yield from page.get("Contents", [])


def read_json(s3, key):
    return json.loads(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, help="only load the last N days (default: everything)")
    args = p.parse_args()

    cutoff = date.today() - timedelta(days=args.days - 1) if args.days else None
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=args.days) if args.days else None

    s3 = get_s3()
    conn = get_conn()
    init_schema(conn)

    loaded = 0
    for table in DAILY_TABLES:
        for obj in list_objects(s3, f"raw/{table}/"):
            day = obj["Key"].rsplit("/", 1)[-1].removesuffix(".json")
            if cutoff and date.fromisoformat(day) < cutoff:
                continue
            upsert_daily(conn, table, day, read_json(s3, obj["Key"]))
            loaded += 1

    acts = [
        read_json(s3, o["Key"])
        for o in list_objects(s3, "raw/activities/")
        if not cutoff_dt or o["LastModified"] >= cutoff_dt
    ]
    if acts:
        upsert_activities(conn, acts)

    conn.close()
    print(f"loaded daily objects={loaded} activities={len(acts)}")


if __name__ == "__main__":
    main()
