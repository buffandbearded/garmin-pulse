"""Integration tests for the S3 data lake layer (needs an S3 endpoint)."""
import json
import os

import pytest
from lake import BUCKET, get_s3, put_activities, put_json

pytestmark = pytest.mark.skipif(
    not os.getenv("AWS_ENDPOINT_URL"), reason="needs an S3 endpoint"
)


def test_bucket_provisioned_with_versioning():
    s3 = get_s3()
    names = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    assert BUCKET in names
    assert s3.get_bucket_versioning(Bucket=BUCKET)["Status"] == "Enabled"


def test_put_json_roundtrip():
    s3 = get_s3()
    key = put_json(s3, "ci_test", "2026-01-01", {"steps": 123})
    body = json.loads(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read())
    assert body == {"steps": 123}
    s3.delete_object(Bucket=BUCKET, Key=key)


def test_put_activities_keyed_by_id():
    s3 = get_s3()
    assert put_activities(s3, [{"activityId": 1, "x": 1}, {"activityId": 2}]) == 2
    prefix = "raw/activities/"
    keys = {o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix).get("Contents", [])}
    assert {f"{prefix}1.json", f"{prefix}2.json"} <= keys
    for k in (f"{prefix}1.json", f"{prefix}2.json"):
        s3.delete_object(Bucket=BUCKET, Key=k)
