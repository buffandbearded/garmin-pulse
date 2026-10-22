"""Daily Garmin pipeline: ingest raw JSON -> dbt build (staging + marts)."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "kristijan",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="garmin_daily",
    description="Ingest Garmin data into raw.*, then build dbt models",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["garmin", "elt"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_garmin",
        bash_command=(
            "cd /opt/airflow/ingestion && "
            "GARMIN_TOKEN_DIR=/opt/airflow/.garmin_tokens "
            "python ingest.py --days 3"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "/home/airflow/dbt-venv/bin/dbt build "
            "--target-path /tmp/dbt_target --log-path /tmp/dbt_logs"
        ),
    )

    ingest >> dbt_build
