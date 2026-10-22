"""Daily Garmin pipeline: ingest to S3 -> load to Postgres -> dbt build."""
from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator

from airflow import DAG

default_args = {
    "owner": "kristijan",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="garmin_daily",
    description="Garmin API -> S3 data lake -> Postgres raw -> dbt models",
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

    load = BashOperator(
        task_id="load_to_postgres",
        bash_command="cd /opt/airflow/ingestion && python load_from_s3.py --days 3",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "/home/airflow/dbt-venv/bin/dbt build "
            "--target-path /tmp/dbt_target --log-path /tmp/dbt_logs"
        ),
    )

    ingest >> load >> dbt_build
