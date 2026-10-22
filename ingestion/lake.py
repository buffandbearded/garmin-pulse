"""S3 data lake helpers. Works against an emulator or real AWS.

Set AWS_ENDPOINT_URL to target an emulator (e.g. http://localhost:4566).
Leave it empty to use real AWS with normal credentials.
"""
import json
import os

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.getenv("S3_BUCKET", "garmin-pulse-raw")


def get_s3():
    endpoint = os.getenv("AWS_ENDPOINT_URL") or None
    kwargs = {"region_name": os.getenv("AWS_REGION", "eu-central-1")}
    if endpoint:
        kwargs.update(
            endpoint_url=endpoint,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            config=Config(s3={"addressing_style": "path"}),
        )
    return boto3.client("s3", **kwargs)


def put_json(s3, endpoint: str, day: str, payload) -> str:
    key = f"raw/{endpoint}/{day}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json",
    )
    return key


def put_activities(s3, activities: list) -> int:
    for a in activities:
        s3.put_object(
            Bucket=BUCKET,
            Key=f"raw/activities/{a['activityId']}.json",
            Body=json.dumps(a).encode("utf-8"),
            ContentType="application/json",
        )
    return len(activities)
